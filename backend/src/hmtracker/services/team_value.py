from datetime import datetime
from hmtracker.database.repository import RepositorySession
from pydantic import BaseModel
from sqlalchemy import text


class TeamValue(BaseModel):
    at: datetime
    value: float
    theorical_value: float


class TeamModification(BaseModel):
    team_id: int  # ID of the Team row in the database
    replaced_player_id: int  # Player ID to use instead of the original player


class _ModifiedTeam(BaseModel):
    player_id: int
    from_datetime: datetime | None
    to_datetime: datetime | None


def compute_team_value_sql(
    repository: RepositorySession,
    manager_id: int,
    season_id: int,
    team_code: str,
    modifications: list[TeamModification] | None = None,
) -> list[TeamValue]:
    """
    Compute the total value of a team at each match date and current date using a single SQL query.

    This is an optimized version of compute_team_value that uses CTEs to perform all
    computations in a single database query instead of multiple round-trips.

    Args:
        repository: Database session
        manager_id: Manager's ID
        season_id: Season's ID
        team_code: Team code
        modifications: Optional list of modifications to simulate player replacements

    Returns:
        List of TeamValue objects with value and theoretical_value at each computation date
    """
    current_date = datetime.now()

    # Build the CASE statement for modifications dynamically
    modification_mapping = {
        modif.team_id: modif.replaced_player_id for modif in modifications or []
    }

    # Build CASE WHEN clauses for player modifications
    if modification_mapping:
        case_clauses = "\n".join(
            f"            WHEN t.id = {team_id} THEN {new_player_id}"
            for team_id, new_player_id in modification_mapping.items()
        )
        player_id_expr = f"""CASE
{case_clauses}
            ELSE t.player_id
        END"""
    else:
        player_id_expr = "t.player_id"

    query = f"""
    WITH computation_dates AS (
        -- All match dates for the season up to now
        SELECT DISTINCT match_datetime AS computation_date
        FROM "MATCHES"
        WHERE match_datetime <= :current_date

        UNION

        -- Current date
        SELECT :current_date AS computation_date
    ),

    modified_team AS (
        -- Apply modifications to team entries
        SELECT
            t.id AS team_entry_id,
            {player_id_expr} AS player_id,
            t.from_datetime,
            t.to_datetime
        FROM "TEAM" t
        WHERE t.manager_id = :manager_id
          AND t.season_id = :season_id
          AND t.team = :team_code
    ),

    active_players AS (
        -- For each computation date, find which players were active
        SELECT
            cd.computation_date,
            mt.player_id
        FROM computation_dates cd
        CROSS JOIN modified_team mt
        WHERE (mt.from_datetime IS NULL OR mt.from_datetime <= cd.computation_date)
          AND (mt.to_datetime IS NULL OR mt.to_datetime >= cd.computation_date)
    ),

    max_validity_dates AS (
        -- Find the most recent stats for each player at each computation date
        SELECT
            ap.computation_date,
            ap.player_id,
            MAX(ps.validity_date) AS max_validity_date
        FROM active_players ap
        JOIN "HOCKEY_PLAYER_STATS" ps
            ON ps.player_id = ap.player_id
            AND ps.season_id = :season_id
            AND ps.validity_date <= ap.computation_date
        GROUP BY ap.computation_date, ap.player_id
    ),

    player_stats_at_date AS (
        -- Get the actual stats records for each player at each date
        SELECT
            mvd.computation_date,
            ps.player_id,
            ps.price,
            ps.hm_points,
            ps.appearances
        FROM max_validity_dates mvd
        JOIN "HOCKEY_PLAYER_STATS" ps
            ON ps.player_id = mvd.player_id
            AND ps.validity_date = mvd.max_validity_date
            AND ps.season_id = :season_id
    )

    -- Final aggregation: compute total value and theoretical value per date
    SELECT
        computation_date AS at,
        SUM(price) AS value,
        SUM(
            CASE
                WHEN appearances IS NOT NULL
                     AND appearances > 0
                     AND hm_points IS NOT NULL
                THEN hm_points / appearances
                ELSE price
            END
        ) AS theorical_value
    FROM player_stats_at_date
    GROUP BY computation_date
    HAVING COUNT(player_id) > 0
    ORDER BY computation_date;
    """

    # Execute the query
    result = repository.session.execute(
        text(query),
        {
            "current_date": current_date,
            "manager_id": manager_id,
            "season_id": season_id,
            "team_code": team_code,
        },
    )

    # Convert to TeamValue objects
    return [
        TeamValue(at=row.at, value=row.value, theorical_value=row.theorical_value)
        for row in result
    ]
