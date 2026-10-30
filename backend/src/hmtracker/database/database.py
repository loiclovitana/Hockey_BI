from sqlalchemy import create_engine, Engine, event

from sqlalchemy.orm import sessionmaker, Session


def init_engine(database_url: str) -> Engine:
    """
    Initialize the database engine
    :param database_url: url of the database to connect to
    :return: the database engine
    """
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _connection_record):
            dbapi_connection.execute("PRAGMA foreign_keys=ON").close()

    return engine


def init_session_maker(database_url: str) -> sessionmaker[Session]:
    """
    Initialize the database session maker
    :param database_url: url of the database to connect to
    :return: A session maker that create a session to the database
    """
    engine = init_engine(database_url)
    db_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    engine.dispose()
    return db_session_maker
