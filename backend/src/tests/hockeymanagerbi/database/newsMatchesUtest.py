import importlib.util
import unittest
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hmtracker.database.models import (
    HockeyPlayer,
    NewsPlayerMatch,
    NewsTeamMatch,
    PlayerInfoType,
    PlayerNews,
    Season,
)


class TestNewsMatchMigration(unittest.TestCase):
    def setUp(self):
        def load_migration(filename, class_name):
            path = Path(__file__).resolve().parents[4] / "migrations/changes" / filename
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name)()

        self.news_migration = load_migration(
            "2026_10_22_000_add_player_news_table.py", "AddPlayerNewsTableMigration"
        )
        self.team_migration = load_migration(
            "2026_10_29_002_add_news_team_match_table.py",
            "AddNewsTeamMatchTableMigration",
        )
        self.player_migration = load_migration(
            "2026_10_29_003_add_news_player_match_table.py",
            "AddNewsPlayerMatchTableMigration",
        )
        self.engine = create_engine("sqlite://")
        event.listen(
            self.engine,
            "connect",
            lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"),
        )
        self.addCleanup(self.engine.dispose)
        for model in (Season, HockeyPlayer):
            model.__table__.create(self.engine)
        self.session = Session(self.engine)
        self.addCleanup(self.session.close)
        self.news_migration.up(self.session)
        self.session.add(
            Season(id=1, name="Current", start=date.today(), end=date.today())
        )
        self.session.flush()
        self.session.add(
            HockeyPlayer(id=1, season_id=1, name="Test P.", role="FW", foreigner=False)
        )
        self.session.flush()
        self.session.add(
            PlayerNews(
                id=1,
                player_id=1,
                season_id=1,
                player_name="Test Player",
                title="News",
                source="https://example.com",
                news_date=date.today(),
                confirmed=True,
                info_type=PlayerInfoType.INJURY,
                availability_time="Tomorrow",
            )
        )
        self.session.commit()
        self.team_migration.up(self.session)
        self.player_migration.up(self.session)
        self.session.commit()

    def test_migrated_news_accepts_null_timing_and_preserves_existing_news(self):
        columns = {
            column["name"]: column
            for column in inspect(self.engine).get_columns("PLAYER_NEWS")
        }
        for name in (
            "season_id",
            "player_id",
            "current_team",
            "new_team",
            "availability_time",
        ):
            self.assertTrue(columns[name]["nullable"], name)
            self.assertTrue(PlayerNews.__table__.c[name].nullable, name)
        self.assertEqual(self.session.get(PlayerNews, 1).availability_time, "Tomorrow")
        self.assertIn(
            "ix_PLAYER_NEWS_source",
            {
                index["name"]
                for index in inspect(self.engine).get_indexes("PLAYER_NEWS")
            },
        )
        for index, kind in enumerate(
            (PlayerInfoType.TRANSFERT, PlayerInfoType.ABSENCE, PlayerInfoType.RETURN),
            start=2,
        ):
            self.session.add(
                PlayerNews(
                    id=index,
                    player_name="Test Player",
                    title="Timing unstated",
                    source=f"https://example.com/{index}",
                    news_date=date.today(),
                    confirmed=True,
                    info_type=kind,
                    availability_time=None,
                )
            )
        self.session.commit()
        self.assertEqual(
            self.session.execute(
                text(
                    "SELECT availability_time FROM PLAYER_NEWS WHERE id > 1 ORDER BY id"
                )
            )
            .scalars()
            .all(),
            [None, None, None],
        )

    def test_news_rollback_drops_only_news_table(self):
        self.session.get(PlayerNews, 1).availability_time = None
        self.session.commit()
        self.news_migration.down(self.session)
        self.session.commit()
        tables = inspect(self.engine).get_table_names()
        self.assertNotIn("PLAYER_NEWS", tables)
        self.assertIn("NEWS_TEAM_MATCH", tables)
        self.assertIn("NEWS_PLAYER_MATCH", tables)
        self.assertIsNotNone(self.session.get(HockeyPlayer, (1, 1)))

    def test_migrated_tables_accept_orm_records_and_preserve_news_links(self):
        self.session.add_all(
            [
                NewsTeamMatch(team_name="city lions", team_code="ZSC"),
                NewsPlayerMatch(
                    player_name="test player", team_code="ZSC", season_id=1, player_id=1
                ),
            ]
        )
        self.session.commit()
        self.assertEqual(self.session.get(NewsTeamMatch, "city lions").team_code, "ZSC")
        self.assertEqual(
            self.session.get(NewsPlayerMatch, ("test player", "ZSC", 1)).player_id, 1
        )
        self.assertEqual(self.session.get(PlayerNews, 1).player_id, 1)

    def test_player_cache_enforces_player_and_season_foreign_key(self):
        self.session.add(
            Season(id=2, name="Other", start=date.today(), end=date.today())
        )
        self.session.commit()
        self.session.add(
            NewsPlayerMatch(
                player_name="test player", team_code="ZSC", season_id=2, player_id=1
            )
        )
        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()

    def test_rollback_preserves_existing_news_and_players(self):
        self.player_migration.down(self.session)
        self.team_migration.down(self.session)
        self.session.commit()
        tables = inspect(self.engine).get_table_names()
        self.assertNotIn("NEWS_TEAM_MATCH", tables)
        self.assertNotIn("NEWS_PLAYER_MATCH", tables)
        self.assertEqual(self.session.get(PlayerNews, 1).player_id, 1)
        self.assertIsNotNone(self.session.get(HockeyPlayer, (1, 1)))

    def test_player_match_uses_team_code_in_primary_key(self):
        schema = inspect(self.engine)
        columns = {column["name"] for column in schema.get_columns("NEWS_PLAYER_MATCH")}
        self.assertIn("team_code", columns)
        self.assertNotIn("team_name", columns)
        self.assertEqual(
            schema.get_pk_constraint("NEWS_PLAYER_MATCH")["constrained_columns"],
            ["player_name", "team_code", "season_id"],
        )

    def test_each_match_migration_rolls_back_only_its_table(self):
        for migration, removed, retained in (
            (self.player_migration, "NEWS_PLAYER_MATCH", "NEWS_TEAM_MATCH"),
            (self.team_migration, "NEWS_TEAM_MATCH", "NEWS_PLAYER_MATCH"),
        ):
            with self.subTest(table=removed):
                migration.down(self.session)
                self.session.commit()
                tables = inspect(self.engine).get_table_names()
                self.assertNotIn(removed, tables)
                self.assertIn(retained, tables)
                self.assertEqual(self.session.get(PlayerNews, 1).player_id, 1)
                migration.up(self.session)
                self.session.commit()
