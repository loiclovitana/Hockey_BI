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
    if current_season is None:
        print("Warning: No season are opened.")

    players_id = [player.id for player in players]
    existing_players: set[int] = {player.id
                                  for player in repository_session.get_players(players_id, current_season.id)}

    new_players = []
    for player in players:
        if player.id not in existing_players:
            existing_players.add(player.id)
            if player.season_id is None:
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
    :param comment: comment related to the importation ignored if importation object is provided
    :return:
    """
    if importation is None:
        importation = models.StatImport(origin=origin,
                                        comment=comment)

    repository_session.session.begin_nested()

    _attach_seasons(repository_session, players, players_stats)

    import_new_players(repository_session, players)

    _import_stats(repository_session, importation, players_stats)

    repository_session.session.commit()


def _import_stats(database_session, importation, players_stats):
    database_session.session.begin_nested()
    current_season: models.Season = database_session.get_current_season()

    for stats in players_stats:
        stats.importation = importation
        if stats.season_id is None:
            stats.season_id = current_season.id
        if stats.validity_date is None:
            stats.validity_date = datetime.now()

    database_session.session.add(importation)
    database_session.session.commit()


def _attach_seasons(database_session: RepositorySession
                    , players: list[models.HockeyPlayer]
                    , players_stats: list[models.HockeyPlayerStats]
                    , arcade=False):
    if len(players) != len(players_stats):
        raise IndexError("There should be one player for each stats")

    all_validity_date = {stats.validity_date for stats in players_stats if stats.validity_date is not None}
    season_for_date = {validity_date: database_session.find_season(validity_date, arcade)
                       for validity_date in all_validity_date}

    for player, stats in zip(players, players_stats):
        if stats.validity_date is None:
            continue
        season_id = season_for_date[stats.validity_date].id
        player.season_id = season_id
        stats.season_id = season_id
