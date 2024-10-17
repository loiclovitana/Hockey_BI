import argparse
import csv
import sys
from datetime import date
from os import getenv
from typing import Any

from sqlalchemy.orm import Session

from HMDataLoader.constants import HM_DATABASE_URL_ENV_NAME
from HMDataLoader.mapper import map_player_stats
from HMDataLoader.player_stats_importer import import_hockey_stats_data
from HMDatabase import repository, models
from HMDatabase.repository import RepositorySession, create_repository_session_maker

__DELIMITER = ';'
__ENCODING = 'utf-8-sig'


def __batch(iterable, batch_size=1):
    length = len(iterable)
    for start_index in range(0, length, batch_size):
        yield iterable[start_index:min(start_index + batch_size, length)]


def __connect_session(db_access: str | Session | RepositorySession) -> RepositorySession:
    if isinstance(db_access, str):
        return create_repository_session_maker(db_access)()
    if isinstance(db_access, Session):
        return RepositorySession(db_access)
    if isinstance(db_access, RepositorySession):
        return db_access
    raise ValueError("Database session must be provided")


def import_csv_to_db(csv_file_path, db_access: Session | str):
    """
    import a csv file containing the player stats into the database tables.
    Close the session once finished
    :param csv_file_path:
    :param db_access: url of database or opened session
    :return:
    """
    players_csv_data = load_csv(csv_file_path)

    players, players_stats = map_player_stats(players_csv_data)

    database_session: RepositorySession = __connect_session(db_access)
    import_hockey_stats_data(database_session, players, players_stats, origin="CSV")
    database_session.end_session()


def load_csv(csv_file_path: str) -> list[dict[str, str]]:
    with open(csv_file_path, encoding=__ENCODING) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=__DELIMITER, quotechar='"')
        return list(reader)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(
        description="Load data from CSV file into a database"
    )

    argument_parser.add_argument("-d", "--database-url",
                                 default=getenv(HM_DATABASE_URL_ENV_NAME),
                                 help=f"""Connection string to connect to the database were to save the data.
                                     If not set, use environment variable {HM_DATABASE_URL_ENV_NAME}""")
    argument_parser.add_argument("-s", "--source_csv", required=True,
                                 help=f"""Path of CSV file to import. Encoding needs to be {__ENCODING}""")

    arguments = argument_parser.parse_args()

    if arguments.database_url is None:
        print(f"Error: Missing argument 'database-url'.")
        argument_parser.print_help()
        sys.exit(1)

    import_csv_to_db(arguments.source_csv, arguments.database_url)
