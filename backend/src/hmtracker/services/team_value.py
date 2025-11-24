from datetime import datetime
from hmtracker.database.repository import RepositorySession
from pydantic import BaseModel


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


def compute_team_value(
    repository: RepositorySession,
    manager_id: int,
    season_id: int,
    team_code: str,
    modifications: list[TeamModification] | None = None,
) -> list[TeamValue]:
    """
    Compute the total value of a team at each match date (up to current date) and at the current date.

    Args:
        repository: Database session
        manager_id: Manager's ID
        season_id: Season's ID
        team_code: Team code
        modifications: Optional list of modifications to simulate player replacements (not saved to DB)

    Returns:
        List of TeamValue objects with value and theoretical_value at each match date and current date
    """
    team_entries = repository.get_team(manager_id, season_id, team_code)

    if not team_entries:
        return []

    modified_player = {
        modif.team_id: modif.replaced_player_id for modif in modifications or []
    }
    modified_entries = [
        _ModifiedTeam(
            player_id=modified_player.get(team.id, team.player_id),
            from_datetime=team.from_datetime,
            to_datetime=team.to_datetime,
        )
        for team in team_entries
    ]

    # Get all matches for the season (up to current date)
    matches = repository.get_matches_for_season(season_id)

    # Collect all computation dates: match dates + current date
    computation_dates = [match.match_datetime for match in matches]
    current_date = datetime.now()

    # Add current date if it's not already in the list
    if not computation_dates or computation_dates[-1].date() != current_date.date():
        computation_dates.append(current_date)

    results = []

    for computation_date in computation_dates:
        # Find which players were in the team at this date
        active_player_ids = []
        for team_entry in modified_entries:
            # from_datetime=None means from beginning, to_datetime=None means until now
            from_date = (
                team_entry.from_datetime if team_entry.from_datetime else datetime.min
            )
            to_date = team_entry.to_datetime if team_entry.to_datetime else datetime.max

            if from_date <= computation_date <= to_date:
                active_player_ids.append(team_entry.player_id)

        if not active_player_ids:
            # No players in the team at this date, skip
            continue

        # Get stats for these players at this date
        player_stats = repository.get_player_stats_at_date(
            active_player_ids, computation_date, season_id
        )

        # Compute actual value and theoretical value
        total_value = 0.0
        total_theoretical_value = 0.0

        for stats in player_stats:
            # Actual value is the sum of prices
            total_value += stats.price

            # Theoretical value: HM_points / Appearances, or price if appearances is None/0
            if (
                stats.appearances is not None
                and stats.appearances > 0
                and stats.hm_points is not None
            ):
                total_theoretical_value += stats.hm_points / stats.appearances
            else:
                # Use actual price if we can't compute theoretical value
                total_theoretical_value += stats.price

        results.append(
            TeamValue(
                at=computation_date,
                value=total_value,
                theorical_value=total_theoretical_value,
            )
        )

    return results
