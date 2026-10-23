import unittest
from datetime import date
from unittest.mock import Mock, patch

from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from hmtracker.database.models import PlayerInfoType, PlayerNews
from hmtracker.database.repository import RepositorySession
from hmtracker.loader.playernews.extractor import (
    ArticlePlayerNews,
    PlayerAbsenceInfo,
    PlayerReturnInfo,
    PlayerTransferInfo,
)
from hmtracker.loader.playernews.importer import import_player_news
from hmtracker.parser.models import ArticleDetails


class TestPlayerNews(unittest.TestCase):
    def setUp(self):
        self.updates = [
            (
                "Transfert",
                PlayerTransferInfo,
                {
                    "from_team": "Old Team",
                    "to_team": "New Team",
                    "transfer_time": "Next season",
                },
            ),
            (
                "Injury",
                PlayerAbsenceInfo,
                {"team": "Team A", "expected_return": "Two weeks"},
            ),
            (
                "Suspension",
                PlayerAbsenceInfo,
                {"team": "Team B", "expected_return": "Three games"},
            ),
            (
                "Absence",
                PlayerAbsenceInfo,
                {"team": None, "expected_return": "Unknown"},
            ),
            ("Return", PlayerReturnInfo, {"team": "Team C", "return_time": "Tonight"}),
            (
                "Transfert",
                PlayerTransferInfo,
                {"from_team": None, "to_team": None, "transfer_time": "Unknown"},
            ),
        ]
        self.players = [
            {
                "player_name": f"  Player {index}  ",
                "rumor": index == 0,
                "info_type": kind,
                **fields,
            }
            for index, (kind, _, fields) in enumerate(self.updates)
        ]

    def test_news_types_select_their_variant_and_round_trip(self):
        result = ArticlePlayerNews.model_validate({"players": self.players})
        for index, ((_, variant, _), player) in enumerate(
            zip(self.updates, result.players)
        ):
            self.assertIsInstance(player, variant)
            self.assertEqual(player.player_name, f"Player {index}")
        self.assertEqual(
            ArticlePlayerNews.model_validate_json(
                result.model_dump_json(), strict=True
            ),
            result,
        )

    def test_variants_reject_other_team_fields_and_missing_required_fields(self):
        for payload, (_, _, fields) in zip(self.players, self.updates):
            invalid_field = "team" if payload["info_type"] == "Transfert" else "to_team"
            with self.subTest(kind=payload["info_type"], extra=invalid_field):
                with self.assertRaises(ValidationError):
                    ArticlePlayerNews.model_validate(
                        {"players": [{**payload, invalid_field: "Other Team"}]}
                    )
            for field in ("player_name", "info_type", *fields):
                with self.subTest(kind=payload["info_type"], missing=field):
                    incomplete = {
                        key: value for key, value in payload.items() if key != field
                    }
                    with self.assertRaises(ValidationError):
                        ArticlePlayerNews.model_validate({"players": [incomplete]})
            timing_field = next(
                key for key in fields if key not in ("team", "from_team", "to_team")
            )
            for field in ("player_name", timing_field):
                with self.subTest(kind=payload["info_type"], blank=field):
                    with self.assertRaises(ValidationError):
                        ArticlePlayerNews.model_validate(
                            {"players": [{**payload, field: "  "}]}
                        )

    @patch("hmtracker.loader.playernews.importer.SwissHockeyNewsParser")
    def test_importer_persists_all_variants_in_existing_db_columns(
        self, parser_factory
    ):
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        PlayerNews.__table__.create(engine)
        article = ArticleDetails(
            date=date(2026, 10, 23),
            title="Player updates",
            description="News",
            text="Updates",
        )
        source = "https://example.com/player-news"
        parser = parser_factory.return_value
        parser.list_news.return_value = [Mock(url=source)]
        parser.article_details.return_value = article
        extractor = Mock(
            return_value=ArticlePlayerNews.model_validate({"players": self.players})
        )

        with RepositorySession(Session(engine)) as repository:
            self.assertEqual(
                import_player_news(repository, extractor), len(self.players)
            )
            records = repository.session.scalars(
                select(PlayerNews).order_by(PlayerNews.id)
            ).all()
            self.assertEqual(
                [
                    (record.current_team, record.new_team, record.availability_time)
                    for record in records
                ],
                [
                    ("Old Team", "New Team", "Next season"),
                    ("Team A", None, "Two weeks"),
                    ("Team B", None, "Three games"),
                    (None, None, "Unknown"),
                    ("Team C", None, "Tonight"),
                    (None, None, "Unknown"),
                ],
            )
            for index, record in enumerate(records):
                self.assertEqual(record.player_name, f"Player {index}")
                self.assertEqual(record.rumor, index == 0)
                self.assertEqual(
                    record.info_type, PlayerInfoType(self.updates[index][0])
                )
                self.assertEqual(
                    (record.source, record.news_date, record.title),
                    (source, article.date, article.title),
                )
        extractor.assert_called_once_with(article)
        parser.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
