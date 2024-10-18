from datetime import datetime

from hockeymanagerbi.database import models
from hockeymanagerbi.database.repository import RepositorySession


def import_new_players(repository_session: RepositorySession
                       , players: list[models.HockeyPlayer]):
    """
    Import the players into the repository
    :param repository_session:
    :param players:
    :return:
    """
    repository_session.session.begin_nested()
    current_season: models.Season = repository_session.get_current_season()

    players_id = [player.id for player in players]
    existing_players: set[int] = {player.id
                                  for player in repository_session.get_players(players_id, current_season.id)}

    new_players = []
    for player in players:
        if player.id not in existing_players:
            existing_players.add(player.id)
            # TODO set correct season for past data
            player.season_id = current_season.id
            new_players.append(player)

    repository_session.session.add_all(new_players)
    repository_session.session.commit()


def import_hockey_stats_data(repository_session: RepositorySession
                             , players: list[models.HockeyPlayer]
                             , players_stats: list[models.HockeyPlayerStats]
                             , importation: models.StatImport | None = None
                             , origin: str = "Unknown"
                             , comment: str = ""
                             ):
    """
    Import the hockey player stats into the database.
    Create the players that doesn't yet exist.
    :param repository_session:
    :param players:
    :param players_stats:
    :param importation: importation object in database
    :param origin: indicates the origin of the importation. ignored if importation object is provided
    :param comment: added in database. ignored if importation object is provided
    :return:
    """
    if importation is None:
        importation = models.StatImport(origin=origin,
                                        comment=comment)

    repository_session.session.begin_nested()

    import_new_players(repository_session, players)

    _import_stats(repository_session, importation, players_stats)

    repository_session.session.commit()


def _import_stats(database_session, importation, players_stats):
    database_session.session.begin_nested()
    current_season: models.Season = database_session.get_current_season()

    for stats in players_stats:
        stats.season_id = current_season.id  # TODO set correct season for past data
        stats.importation = importation
        if stats.validity_date is None:
            stats.validity_date = datetime.now()

    database_session.session.add(importation)
    database_session.session.commit()
