import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hmtracker.database.database import init_engine, init_session_maker
from hmtracker.database.models import (
    HMDatabaseObject,
    HockeyPlayer,
    NewsArticle,
    NewsPlayerMatch,
    PlayerInfoType,
    PlayerNews,
    Season,
)


class TestDatabaseForeignKeys(unittest.TestCase):
    def test_application_sessions_reject_player_links_from_another_season(self):
        maker = init_session_maker("sqlite://")
        with maker() as session:
            engine = session.get_bind()
            self.addCleanup(engine.dispose)
            HMDatabaseObject.metadata.create_all(engine)
            session.add_all(
                [
                    Season(id=1, name="Current", start=date.today(), end=date.today()),
                    Season(
                        id=2, name="Old", start=date(2000, 1, 1), end=date(2001, 1, 1)
                    ),
                ]
            )
            session.flush()
            session.add(
                HockeyPlayer(
                    id=99, season_id=2, name="Test P.", role="FW", foreigner=False
                )
            )
            article = NewsArticle(
                base_url="https://example.com",
                article_url="/test",
                article_date=date.today(),
                title="News",
            )
            session.add(article)
            session.commit()

            for record in (
                NewsPlayerMatch(
                    player_name="test player",
                    team_code="ZSC",
                    season_id=1,
                    player_id=99,
                ),
                PlayerNews(
                    article_id=article.id,
                    player_name="Test Player",
                    info_type=PlayerInfoType.INJURY,
                    season_id=1,
                    player_id=99,
                ),
            ):
                with self.subTest(table=record.__tablename__):
                    with self.assertRaises(IntegrityError), session.begin_nested():
                        session.add(record)
                        session.flush()

            session.add(
                NewsPlayerMatch(
                    player_name="test player",
                    team_code="ZSC",
                    season_id=2,
                    player_id=99,
                )
            )
            session.commit()

    def test_foreign_keys_are_enabled_for_each_new_connection(self):
        with TemporaryDirectory() as directory:
            engine = init_engine(f"sqlite:///{Path(directory) / 'database.sqlite'}")
            try:
                # Concurrent checkouts require separate physical connections.
                with engine.connect() as first, engine.connect() as second:
                    for connection in (first, second):
                        self.assertEqual(
                            connection.exec_driver_sql("PRAGMA foreign_keys").scalar(),
                            1,
                        )
                engine.dispose()
                with Session(engine) as session:
                    self.assertEqual(
                        session.connection()
                        .exec_driver_sql("PRAGMA foreign_keys")
                        .scalar(),
                        1,
                    )
            finally:
                engine.dispose()
