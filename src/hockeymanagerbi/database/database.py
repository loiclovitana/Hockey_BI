from sqlalchemy import create_engine, Engine

from sqlalchemy.orm import sessionmaker, Session


def init_engine(database_url: str) -> Engine:
    """
    Initialize the database engine
    :param database_url: url of the database to connect to
    :return: the database engine
    """
    engine = create_engine(
        database_url, connect_args={"check_same_thread": False}
    )
    return engine


def init_session_maker(database_url: str) -> sessionmaker[Session]:
    """
    Initialize the database session maker
    :param database_url: url of the database to connect to
    :return: A session maker that create a session to the database
    """
    engine = init_engine(database_url)
    db_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return db_session_maker
