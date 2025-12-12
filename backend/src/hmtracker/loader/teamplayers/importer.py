import logging
from datetime import datetime
from hmtracker.database import models
from hmtracker.database.repository import RepositorySession


def import_manager(
    repository_session: RepositorySession, user_email: str
) -> models.Manager:
    manager = models.Manager(email=user_email)
    repository_session.session.begin_nested()
    repository_session.session.add(manager)
    repository_session.session.commit()
    return manager


def import_team(
    repository_session: RepositorySession,
    manager: models.Manager,
    team_code: str,
    current_players_ids: list[int],
    at_datetime: datetime | None = None,
):
    current_players_ids = [int(player_id) for player_id in current_players_ids]
    if at_datetime is None:
        at_datetime = datetime.now()

    repository_session.session.begin_nested()
    current_season: models.Season = repository_session.find_season(at_datetime)
    if current_season is None:
        logging.warning("No season are currently opened")

    season_team = repository_session.get_team(manager, current_season, team_code)

    actual_team = [p for p in season_team if p.to_datetime is None]

    for actual_team_player in actual_team:
        if (
            actual_team_player.from_datetime is not None
            and actual_team_player.from_datetime >= at_datetime
        ):
            raise Exception(f"Cannot import team before last import : {at_datetime}")

        if actual_team_player.player_id not in current_players_ids:
            actual_team_player.to_datetime = at_datetime

    actual_team_players_id = {
        current_team_player.player_id for current_team_player in actual_team
    }
    new_team_player = [
        models.Team(
            team=team_code,
            manager_id=manager.id,
            player_id=player_id,
            season_id=current_season.id,
            from_datetime=None if len(actual_team) == 0 else at_datetime,
        )
        for player_id in current_players_ids
        if player_id not in actual_team_players_id
    ]
    repository_session.session.add_all(new_team_player)

    manager.last_import = datetime.now()

    repository_session.session.commit()
