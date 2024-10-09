import os
import sys

from HMDatabase.database import create_engine
from HMDatabase import models


def initialize_database(db_url : str):
    """
    Initialize the database by creating all tables objects
    :param db_url:
    :return:
    """
    db_engine = create_engine(db_url)
    models.HMDatabaseObject.metadata.create_all(db_engine)

if __name__ == '__main__':
    database_url = os.getenv('HM_DATABASE_URL')
    if len(sys.argv) >2:
        database_url=sys.argv[1]

    if database_url is None:
        raise Exception('Database URL not provided and environment variable HM_DATABASE_URL is not set')

    initialize_database(database_url)