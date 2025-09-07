import argparse
import logging
import sys
from collections.abc import Callable
from os import getenv

from sqlalchemy.orm import Session

from hmtracker.database.repository import (
    RepositorySession,
    create_repository_session_maker,
)
from hmtracker.database import models
from hmtracker.constants import (
    HM_DATABASE_URL_ENV_NAME,
    HM_USER_ENV_NAME,
    HM_PASSWORD_ENV_NAME,
)
from hmtracker.loader.playerstats.importer import import_hockey_stats_data
from hmtracker.loader.playerstats.mapper import map_player_stats
from hmtracker.loader.playerstats.source.file import __ENCODING, playerstats_csv_loader
from hmtracker.loader.playerstats.source.website import playerstats_ajax_loader
from hmtracker.loader.teamplayers.importer import import_team, import_manager
from hmtracker.loader.teamplayers.source.website import team_players_ajax_loader


def __connect_session(
    db_access: str | Session | RepositorySession,
) -> RepositorySession:
    if isinstance(db_access, str):
        return create_repository_session_maker(db_access)()
    if isinstance(db_access, Session):
        return RepositorySession(db_access)
    if isinstance(db_access, RepositorySession):
        return db_access
    raise ValueError("Database session must be provided")


def import_playerstats_from_ajax(db_access: Session | str, user, password):
    """
    Import data from HockeyManager website
    :param db_access:
    :param user:
    :param password:
    :return:
    """
    ajax_loader = playerstats_ajax_loader(user, password)
    import_playerstats_from_loader(ajax_loader, db_access)


def import_playerstats_from_csv(
    csv_file_path, db_access: Session | str | RepositorySession
):
    """
    import a csv file containing the player stats into the database tables.
    Close the session once finished
    :param csv_file_path:
    :param db_access: url of database or opened session
    :return:
    """
    csv_loader = playerstats_csv_loader(csv_file_path)
    import_playerstats_from_loader(csv_loader, db_access)


def import_playerstats_from_loader(
    playerstats_loader, db_access: Session | str | RepositorySession, origin="Unknown"
):
    players_data = playerstats_loader()
    players, players_stats = map_player_stats(players_data)

    database_session: RepositorySession = __connect_session(db_access)
    import_hockey_stats_data(database_session, players, players_stats, origin=origin)
    if isinstance(db_access, RepositorySession):
        database_session.session.commit()
    else:
        database_session.end_session()


def import_teamplayers_from_loader(
    teamplayers_loader: Callable,
    hm_user_email: str,
    db_access: Session | str | RepositorySession,
):
    team_players: dict[str, list[int]] = teamplayers_loader()

    database_session: RepositorySession = __connect_session(db_access)

    hm_manager: models.Manager | None = database_session.get_manager_by_email(
        hm_user_email
    )
    if hm_manager is None:
        hm_manager = import_manager(database_session, hm_user_email)

    for team_code, players_ids in team_players.items():
        import_team(database_session, hm_manager, team_code, players_ids)

    if isinstance(db_access, RepositorySession):
        database_session.session.commit()
    else:
        database_session.end_session()


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description="Load data from hockey manager using ajax queries into a database"
    )

    argument_parser.add_argument(
        "-d",
        "--database-url",
        default=getenv(HM_DATABASE_URL_ENV_NAME),
        help=f"""Connection string to connect to the database were to save the data.
                             If not set, use environment variable {HM_DATABASE_URL_ENV_NAME}""",
    )
    argument_parser.add_argument(
        "-u",
        "--hm-user",
        default=getenv(HM_USER_ENV_NAME),
        help=f"""User login to connect to Hockey Manager.
                                 If not set, use environment variable {HM_USER_ENV_NAME}""",
    )
    argument_parser.add_argument(
        "-p",
        "--hm-password",
        default=getenv(HM_PASSWORD_ENV_NAME),
        help=f"""Password for login to HockeyManager.
                                 If not set, use environment variable {HM_PASSWORD_ENV_NAME}""",
    )
    argument_parser.add_argument(
        "-s",
        "--source-csv",
        help=f"""If provided, import data from CSV path instead of ajax. Encoding needs to be {__ENCODING}""",
    )

    argument_parser.add_argument(
        "-t",
        "--teams",
        action="store_true",
        help="""If present, import the team of the user instead of the hockey player stats""",
    )

    def check_exists(argument, name):
        if argument is None:
            logging.error(f"Error: Missing argument {name}.")
            argument_parser.print_help()
            sys.exit(1)

    arguments = argument_parser.parse_args()
    check_exists(arguments.database_url, "database-url")
    if arguments.teams:
        if arguments.source_csv is not None:
            raise NotImplementedError(
                "Importation of a team from csv is not implemented"
            )
        loader = team_players_ajax_loader(arguments.hm_user, arguments.hm_password)
        import_teamplayers_from_loader(
            loader, arguments.hm_user, arguments.database_url
        )
        exit(0)

    if arguments.source_csv is not None:
        loader = playerstats_csv_loader(arguments.source_csv)
    else:
        check_exists(arguments.hm_user, "hm-user")
        check_exists(arguments.hm_password, "hm-password")
        loader = playerstats_ajax_loader(arguments.hm_user, arguments.hm_password)

    import_playerstats_from_loader(loader, arguments.database_url)
