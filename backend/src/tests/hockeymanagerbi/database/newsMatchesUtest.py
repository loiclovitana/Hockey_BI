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
        path = (
            Path(__file__).resolve().parents[4]
            / "migrations/changes/2026_10_29_002_add_news_matches.py"
        )
        spec = importlib.util.spec_from_file_location("news_matches_migration", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.migration = module.AddNewsMatchesMigration()
        code_path = path.with_name("2026_10_29_003_rename_player_match_team_code.py")
        code_spec = importlib.util.spec_from_file_location(
            "player_match_team_code_migration", code_path
        )
        code_module = importlib.util.module_from_spec(code_spec)
        code_spec.loader.exec_module(code_module)
        self.code_migration = code_module.RenamePlayerMatchTeamCodeMigration()
        self.engine = create_engine("sqlite://")
        event.listen(
            self.engine,
            "connect",
            lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"),
        )
        self.addCleanup(self.engine.dispose)
        for model in (Season, HockeyPlayer, PlayerNews):
            model.__table__.create(self.engine)
        self.session = Session(self.engine)
        self.addCleanup(self.session.close)
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
        self.migration.up(self.session)
        self.code_migration.up(self.session)
        self.session.commit()

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
        self.code_migration.down(self.session)
        self.migration.down(self.session)
        self.session.commit()
        tables = inspect(self.engine).get_table_names()
        self.assertNotIn("NEWS_TEAM_MATCH", tables)
        self.assertNotIn("NEWS_PLAYER_MATCH", tables)
        self.assertEqual(self.session.get(PlayerNews, 1).player_id, 1)
        self.assertIsNotNone(self.session.get(HockeyPlayer, (1, 1)))

    def test_team_code_rename_preserves_saved_player_decisions(self):
        self.code_migration.down(self.session)
        self.session.execute(
            text("""
            INSERT INTO NEWS_PLAYER_MATCH (player_name, team_name, season_id, player_id)
            VALUES ('test player', 'ZSC', 1, 1)
        """)
        )
        self.session.commit()
        self.code_migration.up(self.session)
        self.session.commit()
        saved = self.session.get(NewsPlayerMatch, ("test player", "ZSC", 1))
        self.assertEqual(saved.team_code, "ZSC")
        self.assertEqual(saved.player_id, 1)
        self.code_migration.down(self.session)
        self.session.commit()
        self.assertEqual(
            self.session.execute(
                text("SELECT team_name, player_id FROM NEWS_PLAYER_MATCH")
            ).one(),
            ("ZSC", 1),
        )
