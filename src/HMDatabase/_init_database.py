import os
import sys

from HMDatabase.database import create_engine, init_session_maker
from HMDatabase import models, crud

from datetime import date

FIRST_SEASON = 2022
MONTH_START_SEASON = 8
MONTH_END_SEASON = 7


def create_seasons(session, from_year: int, to_year: int | None = None):
    today = date.today()
    current_year_season = today.year if today.month > 7 else today.year - 1
    if to_year is None or to_year < 2000:
        to_year = current_year_season + 1

    seasons = [models.Season(name=f"{year}/{year + 1}"
                             , is_current=year == current_year_season
                             , start=date.fromisocalendar(year, MONTH_START_SEASON, 1)
                             , end=date.fromisocalendar(year + 1, MONTH_START_SEASON, 1)
                             )
               for year in range(from_year, to_year)]

    session.add_all(seasons)


def initialize_database(db_url: str):
    """
    Initialize the database by creating all tables objects
    :param db_url:
    :return:
    """
    db_engine = create_engine(db_url)
    models.HMDatabaseObject.metadata.create_all(db_engine)

    session = init_session_maker(db_url)()
    if crud.get_current_season(session) is None:
        create_seasons(session, FIRST_SEASON)

    session.commit()


if __name__ == '__main__':
    database_url = os.getenv('HM_DATABASE_URL')
    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    if database_url is None:
        raise Exception('Database URL not provided and environment variable HM_DATABASE_URL is not set')

    initialize_database(database_url)
