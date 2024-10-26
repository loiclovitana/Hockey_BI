import argparse
import logging
import sys
from os import getenv

from sqlalchemy.orm import Session

from hockeymanagerbi.loader.constants import HM_DATABASE_URL_ENV_NAME, HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME
from hockeymanagerbi.loader.playerstats.source.ajax import playerstats_ajax_loader
from hockeymanagerbi.loader.playerstats.importer import import_hockey_stats_data
from hockeymanagerbi.loader.playerstats.mapper import map_player_stats
from hockeymanagerbi.database.repository import RepositorySession, create_repository_session_maker
from hockeymanagerbi.loader.playerstats.source.file import load_csv, __ENCODING, playerstats_csv_loader


def __connect_session(db_access: str | Session | RepositorySession) -> RepositorySession:
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


def import_playerstats_from_csv(csv_file_path, db_access: Session | str):
    """
    import a csv file containing the player stats into the database tables.
    Close the session once finished
    :param csv_file_path:
    :param db_access: url of database or opened session
    :return:
    """
    csv_loader = playerstats_csv_loader(csv_file_path)
    import_playerstats_from_loader(csv_loader, db_access)


def import_playerstats_from_loader(playerstats_loader, db_access: Session | str, origin="Unknown"):
    players_data = playerstats_loader()
    players, players_stats = map_player_stats(players_data)

    database_session: RepositorySession = __connect_session(db_access)
    import_hockey_stats_data(database_session, players, players_stats, origin=origin)
    if isinstance(db_access, RepositorySession):
        database_session.session.commit()
    else:
        database_session.end_session()


if __name__ == '__main__':

    argument_parser = argparse.ArgumentParser(
        description="Load data from hockey manager using ajax queries into a database"
    )

    argument_parser.add_argument("-d", "--database-url", default=getenv(HM_DATABASE_URL_ENV_NAME)
                                 , help=f"""Connection string to connect to the database were to save the data.
                             If not set, use environment variable {HM_DATABASE_URL_ENV_NAME}""")
    argument_parser.add_argument("-u", "--hm-user", default=getenv(HM_USER_ENV_NAME)
                                 , help=f"""User login to connect to Hockey Manager.
                                 If not set, use environment variable {HM_USER_ENV_NAME}""")
    argument_parser.add_argument("-p", "--hm-password", default=getenv(HM_PASSWORD_ENV_NAME)
                                 , help=f"""Password for login to HockeyManager.
                                 If not set, use environment variable {HM_PASSWORD_ENV_NAME}""")
    argument_parser.add_argument("-s", "--source-csv",
                                 help=f"""If provided, import data from CSV path instead of ajax. Encoding needs to be {__ENCODING}""")


    def check_exists(argument, name):
        if argument is None:
            logging.error(f"Error: Missing argument {name}.")
            argument_parser.print_help()
            sys.exit(1)


    arguments = argument_parser.parse_args()
    check_exists(arguments.database_url, 'database-url')
    if arguments.source_csv is not None:
        loader = playerstats_csv_loader(arguments.source_csv)
    else:
        check_exists(arguments.hm_user, 'hm-user')
        check_exists(arguments.hm_password, 'hm-password')
        loader = playerstats_ajax_loader(arguments.hm_user, arguments.hm_password)

    import_playerstats_from_loader(loader, arguments.database_url)
