from sqlalchemy.orm import Session

from HMDatabase import models
from HMDatabase.repository import RepositorySession, create_repository_session_maker


def __connect_session(db_access: str | Session | RepositorySession) -> RepositorySession:
    if isinstance(db_access, str):
        return create_repository_session_maker(db_access)()
    if isinstance(db_access, Session):
        db_access.begin_nested()
        return RepositorySession(db_access)
    if isinstance(db_access, RepositorySession):
        db_access.session.begin_nested()
        return db_access
    raise ValueError("Database session must be provided")


def import_new_players(db_access: str | Session | RepositorySession
                       , players: list[models.HockeyPlayer]):
    """

    :param db_access:
    :param players:
    :return:
    """
    database_session: RepositorySession = __connect_session(db_access)
    players_id = [player.id for player in players]
    existing_players: set[str] = {player.id
                                  for player in database_session.get_players(players_id, current_season.id)}

    current_season: models.Season = database_session.get_current_season()

    new_players = []
    for player in players:
        if player.id not in existing_players:
            existing_players.add(player.id)
            # TODO set correct season for past data
            player.season_id = current_season.id
            new_players.append(player)

    database_session.session.add_all(new_players)
    database_session.session.commit()


def import_hockey_stats_data(db_access: str | Session | RepositorySession
                             , players: list[models.HockeyPlayer]
                             , players_stats: list[models.HockeyPlayerStats]
                             , origin: str = "Unkown"
                             , comment: str = ""
                             ):
    database_session: RepositorySession = __connect_session(db_access)

    import_new_players(database_session, players)

