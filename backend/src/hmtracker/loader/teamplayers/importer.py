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
    players_ids: list[int],
    at_datetime: datetime = None,
):
    players_ids = [int(player_id) for player_id in players_ids]
    if at_datetime is None:
        at_datetime = datetime.now()

    repository_session.session.begin_nested()
    current_season: models.Season = repository_session.find_season(at_datetime)
    if current_season is None:
        logging.warning("No season are currently opened")

    current_season_team = repository_session.get_team(
        manager, current_season, team_code
    )
    current_players = [
        current_team_player.player_id for current_team_player in current_season_team
    ]
    for current_team_player in current_season_team:
        if (
            current_team_player.from_datetime is not None
            and current_team_player.from_datetime >= at_datetime
        ):
            raise Exception(f"Cannot import team before last import : {at_datetime}")

        if current_team_player.player_id not in players_ids:
            current_team_player.to_datetime = at_datetime

    new_team_player = [
        models.Team(
            team=team_code,
            manager_id=manager.id,
            player_id=player_id,
            season_id=current_season.id,
            from_datetime=None if len(current_season_team) == 0 else at_datetime,
        )
        for player_id in players_ids
        if player_id not in current_players
    ]
    repository_session.session.add_all(new_team_player)

    repository_session.session.commit()
