import csv
import sys
from os import getenv

from sqlalchemy.orm import Session

from HMDatabase import database, crud, models

__INSERTION_BATCH_SIZE = 100


def import_csv_to_db(csv_file_path, db_access: Session | str):
    database_session: Session = __connect_session(db_access)

    current_season: models.Season = crud.get_current_season(database_session)

    imported_dates = crud.get_imported_stats_dates(database_session)
    print(imported_dates)
    with open(csv_file_path) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",", quotechar='"')
        for i, row in enumerate(reader):
            print(row)
            break

    database_session.rollback()


def __connect_session(db_access) -> Session:
    if isinstance(db_access, str):
        return database.init_session_maker(db_access)()
    if isinstance(db_access, Session):
        return db_access

    raise ValueError("Database session must be provided")


if __name__ == '__main__':
    database_url = getenv('HM_DATABASE_URL')
    csv_path = getenv('HM_CSV_IMPORT_PATH')

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    if csv_path is None:
        raise Exception('CSV path is not provided')

    if len(sys.argv) > 2:
        database_url = sys.argv[2]
    if database_url is None:
        raise Exception('Database URL not provided and environment variable HM_DATABASE_URL is not set')

    import_csv_to_db(csv_path, database_url)
