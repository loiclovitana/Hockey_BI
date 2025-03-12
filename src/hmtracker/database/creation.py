import os
import sys
from datetime import date

from hmtracker.database import models
from hmtracker.database.database import create_engine
from hmtracker.database.repository import create_repository_session_maker, RepositorySession

FIRST_SEASON = 2022
MONTH_START_SEASON = 8
MONTH_END_SEASON = 7


def create_seasons(db_url: str, from_year: int, to_year: int | None = None):
    database_session: RepositorySession = create_repository_session_maker(db_url)()
    today = date.today()
    current_year_season = today.year if today.month > 7 else today.year - 1
    if to_year is None or to_year < 2000:
        to_year = current_year_season + 1

    seasons = [models.Season(name=f"{year}/{year + 1}"
                             , start=date(year, MONTH_START_SEASON, 1)
                             , end=date(year + 1, MONTH_END_SEASON, 1)
                             , arcade=False
                             )
               for year in range(from_year, to_year)] + [models.Season(name=f"{year}/{year + 1}"
                                                                       , start=date(year, MONTH_START_SEASON, 1)
                                                                       , end=date(year + 1, MONTH_END_SEASON, 1)
                                                                       , arcade=True
                                                                       )
                                                         for year in range(from_year, to_year)]

    database_session.session.add_all(seasons)
    database_session.end_session()


def initialize_database(db_url: str):
    """
    Initialize the database by creating all tables objects
    :param db_url:
    :return:
    """
    db_engine = create_engine(db_url)
    try:
        models.HMDatabaseObject.metadata.create_all(db_engine)

        create_seasons(db_url, FIRST_SEASON)
    finally:
        db_engine.dispose()


if __name__ == '__main__':
    database_url = os.getenv('HM_DATABASE_URL')
    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    if database_url is None:
        raise Exception('Database URL not provided and environment variable HM_DATABASE_URL is not set')

    initialize_database(database_url)
