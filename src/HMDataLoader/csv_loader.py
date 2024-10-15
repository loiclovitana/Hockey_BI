import argparse
import csv
import sys
from datetime import date
from os import getenv
from typing import Any

from sqlalchemy.orm import Session

from HMDataLoader.constants import HM_DATABASE_URL_ENV_NAME
from HMDatabase import repository, models
from HMDatabase.repository import RepositorySession, create_repository_session_maker

__DELIMITER = ','
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
    database_session: RepositorySession = __connect_session(db_access)

    current_season: models.Season = database_session.get_current_season()

    already_imported_dates = {importation.validity_date: importation for importation in
                              database_session.get_imported_stats_dates()}

    players_id, players_csv_data = load_csv(csv_file_path)
    existing_players = {player.id: player
                        for player in database_session.get_players(list(players_id), current_season.id)}

    # Add new players
    new_players = []
    for player in players_csv_data:
        if player['id'] not in existing_players.keys():
            new_player = models.HockeyPlayer(id=int(player['id'])
                                             , season_id=current_season.id
                                             , name=player['name']
                                             , club=player['club']
                                             , role=player['role'])
            existing_players[player['id']] = new_player
            new_players.append(new_player)

    database_session.session.add_all(new_players)

    # Add imported date
    imported_dates = dict()
    for player in players_csv_data:
        stats_validity_date = player['date']

        if stats_validity_date in already_imported_dates.keys():
            # TODO use parameter if want to check
            # TODO use date instead of timestamp? or maybe dateDiff
            print(
                f"Warning: player stats for is already imported for "
                f"\n\tid={player['id']}"
                f"\n\tdate={stats_validity_date}")
            continue
        if stats_validity_date not in imported_dates.keys():
            imported_dates[stats_validity_date] = models.StatImport(validity_date=stats_validity_date,
                                                                    origin='CSV',
                                                                    comment="Legacy import")
        importation = imported_dates[stats_validity_date]
        player_stats = models.HockeyPlayerStats(
            player_id=player['id']
            , validity_date=stats_validity_date
            , importation=importation
            , price=player['Price']
            , hm_points=player['HM points']
            , appearances=player['Appareances']
            , goal=player['Goal']
            , assists=None if player['Assist #1'] is None
            else player['Assist #1'] + player['Assist #2'] + player['Assist OT']
            , penalties=player['Penalties']
            , plus_minus=player['+/-']
        )

    database_session.session.add_all(list(imported_dates.values()))

    database_session.end_session()


def load_csv(csv_file_path: str):
    def to_float(value: str) -> float:
        return float(value.replace(",", "."))

    def try_convert(field: str, type_cast):
        try:
            return type_cast(field)
        except:
            print(f'Warning: invalid field cannot convert value "{field}" into type <{type_cast.__name__}>')
            return None

    with open(csv_file_path, encoding=__ENCODING) as csv_file:
        reader: csv.DictReader[dict[str, Any]] = csv.DictReader(csv_file, delimiter=__DELIMITER, quotechar='"')
        players_id = set()
        players_csv_data: list[dict[str, Any]] = []
        for player in reader:
            player['id'] = try_convert(player['id'], int)
            player['date'] = try_convert(player['date'], date.fromisoformat)
            player['Price'] = try_convert(player['Price'], to_float)
            player['Ownership'] = try_convert(player['Ownership'].replace('%', ''), to_float)
            player['HM points'] = try_convert(player['HM points'], to_float)
            player['Appareances'] = try_convert(player['Appareances'], int)
            player['Goal'] = try_convert(player['Goal'], int)
            player['Goal OT'] = try_convert(player['Goal OT'], int)
            player['Assist #1'] = try_convert(player['Assist #1'], int)
            player['Assist #2'] = try_convert(player['Assist #2'], int)
            player['Assist OT'] = try_convert(player['Assist OT'], int)
            player['Points'] = try_convert(player['Points'], int)
            player['GWG'] = try_convert(player['GWG'], int)
            player['Penalties'] = try_convert(player['Penalties'], int)
            player['Shots'] = try_convert(player['Shots'], int)

            players_id.add(player['id'])
            players_csv_data.append(player)

        return players_id, players_csv_data


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
