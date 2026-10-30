import os
import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch

from pydantic import ValidationError
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hmtracker.database.models import (
    HMDatabaseObject,
    NewsArticle,
    PlayerInfoType,
    PlayerNews,
)
from hmtracker.database.repository import RepositorySession
from hmtracker.loader.playernews.extractor import (
    ArticlePlayerNews,
    PlayerAbsenceInfo,
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
                "Absence",
                PlayerAbsenceInfo,
                {
                    "reason": "Injury",
                    "team": "Team A",
                    "is_return": False,
                    "expected_duration_or_return": "Two weeks",
                },
            ),
            (
                "Absence",
                PlayerAbsenceInfo,
                {
                    "reason": "Suspension",
                    "team": "Team B",
                    "is_return": False,
                    "expected_duration_or_return": "Three games",
                },
            ),
            (
                "Absence",
                PlayerAbsenceInfo,
                {
                    "reason": None,
                    "team": None,
                    "is_return": False,
                    "expected_duration_or_return": None,
                },
            ),
            (
                "Absence",
                PlayerAbsenceInfo,
                {
                    "reason": "Injury",
                    "team": "Team C",
                    "is_return": True,
                    "expected_duration_or_return": "Tonight",
                },
            ),
            (
                "Transfert",
                PlayerTransferInfo,
                {"from_team": None, "to_team": None, "transfer_time": None},
            ),
        ]
        self.players = [
            {
                "player_name": f"  Player {index}  ",
                "confirmed": index != 0,
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
            self.assertEqual(player.confirmed, index != 0)
            for field, value in self.updates[index][2].items():
                self.assertEqual(getattr(player, field), value)
        self.assertEqual(
            ArticlePlayerNews.model_validate_json(
                result.model_dump_json(), strict=True
            ),
            result,
        )

    def test_variants_reject_other_team_fields_and_missing_required_fields(self):
        for payload in self.players:
            invalid_field = "team" if payload["info_type"] == "Transfert" else "to_team"
            with self.subTest(kind=payload["info_type"], extra=invalid_field):
                with self.assertRaises(ValidationError):
                    ArticlePlayerNews.model_validate(
                        {"players": [{**payload, invalid_field: "Other Team"}]}
                    )
            for field in payload:
                with self.subTest(kind=payload["info_type"], missing=field):
                    incomplete = {
                        key: value for key, value in payload.items() if key != field
                    }
                    with self.assertRaises(ValidationError):
                        ArticlePlayerNews.model_validate({"players": [incomplete]})
            nonempty_fields = ["player_name"]
            if payload["info_type"] == "Absence":
                nonempty_fields.append("expected_duration_or_return")
            for field in nonempty_fields:
                with self.subTest(kind=payload["info_type"], blank=field):
                    with self.assertRaises(ValidationError):
                        ArticlePlayerNews.model_validate(
                            {"players": [{**payload, field: "  "}]}
                        )

    def test_absence_reason_rejects_non_absence_types(self):
        for reason in ("Transfert", "Return", "Absence"):
            with self.subTest(reason=reason), self.assertRaises(ValidationError):
                ArticlePlayerNews.model_validate(
                    {"players": [{**self.players[1], "reason": reason}]}
                )

    def test_absences_reject_legacy_discriminator_values(self):
        for kind in ("Injury", "Suspension", "Return"):
            with self.subTest(kind=kind), self.assertRaises(ValidationError):
                ArticlePlayerNews.model_validate(
                    {"players": [{**self.players[1], "info_type": kind}]}
                )

    @patch("hmtracker.loader.playernews.importer.SwissHockeyNewsParser")
    def test_importer_persists_all_variants_with_one_shared_article(
        self, parser_factory
    ):
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        HMDatabaseObject.metadata.create_all(engine)
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
            stored_article = repository.session.scalars(select(NewsArticle)).one()
            self.assertIsInstance(stored_article.processed_date, datetime)
            self.assertEqual(
                {record.article_id for record in records}, {stored_article.id}
            )
            self.assertEqual(
                [
                    (record.current_team, record.new_team, record.availability_time)
                    for record in records
                ],
                [
                    ("Old Team", "New Team", "Next season"),
                    ("Team A", None, "Two weeks"),
                    ("Team B", None, "Three games"),
                    (None, None, None),
                    ("Team C", None, "Tonight"),
                    (None, None, None),
                ],
            )
            for index, record in enumerate(records):
                self.assertEqual(record.player_name, f"Player {index}")
                self.assertEqual(record.confirmed, index != 0)
                self.assertEqual(
                    record.info_type,
                    [
                        PlayerInfoType.TRANSFERT,
                        PlayerInfoType.INJURY,
                        PlayerInfoType.SUSPENSION,
                        PlayerInfoType.ABSENCE,
                        PlayerInfoType.RETURN,
                        PlayerInfoType.TRANSFERT,
                    ][index],
                )
                self.assertEqual(
                    (
                        record.article.article_url,
                        record.article.article_date,
                        record.article.title,
                    ),
                    ("/player-news", article.date, article.title),
                )
        extractor.assert_called_once_with(article)
        parser.close.assert_called_once_with()


class TestProcessedArticles(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        event.listen(
            self.engine,
            "connect",
            lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"),
        )
        self.addCleanup(self.engine.dispose)
        HMDatabaseObject.metadata.create_all(self.engine)
        self.repository = RepositorySession(Session(self.engine))
        self.addCleanup(self.repository.end_session)
        self.parser = self.enterContext(
            patch("hmtracker.loader.playernews.importer.SwissHockeyNewsParser")
        ).return_value
        self.parser.list_news.return_value = [Mock(url="/en/news/test")]
        self.article = ArticleDetails(
            date=date(2026, 10, 23), title="Article title", description="", text="News"
        )
        self.parser.article_details.return_value = self.article
        self.extractor = Mock(return_value=ArticlePlayerNews(players=[]))
        self.enterContext(
            patch.dict(
                os.environ,
                {
                    "HM_PLAYER_NEWS_PROVIDER": "ollama",
                    "HM_PLAYER_NEWS_MODEL": "test-model",
                },
            )
        )

    def test_empty_article_is_saved_and_never_sent_to_llm_again(self):
        url = "https://swisshockeynews.ch/en/news/test"
        self.parser.list_news.return_value += [Mock(url=url)]
        started = datetime.now()
        self.assertEqual(import_player_news(self.repository, self.extractor), 0)
        with Session(self.engine) as session:
            article = session.scalars(select(NewsArticle)).one()
            self.assertEqual(article.base_url, "https://swisshockeynews.ch")
            self.assertEqual(article.article_url, "/en/news/test")
            self.assertEqual(article.article_date, self.article.date)
            self.assertEqual(article.title, self.article.title)
            self.assertEqual(article.processed_by, "test-model")
            processed_date = article.processed_date
            self.assertGreaterEqual(processed_date, started)
            self.assertLessEqual(processed_date, datetime.now())
            self.assertEqual(session.scalars(select(PlayerNews)).all(), [])
        self.assertEqual(import_player_news(self.repository, self.extractor), 0)
        with Session(self.engine) as session:
            self.assertEqual(
                session.scalar(select(NewsArticle.processed_date)), processed_date
            )
        self.extractor.assert_called_once_with(self.article)
        self.parser.article_details.assert_called_once_with(url)

    def test_successful_articles_commit_while_failed_extractions_are_retried(self):
        self.parser.list_news.return_value = [Mock(url="/good"), Mock(url="/bad")]
        self.extractor.side_effect = [
            ArticlePlayerNews(players=[]),
            RuntimeError("LLM failed"),
        ]
        with self.assertLogs(level="ERROR"):
            self.assertEqual(import_player_news(self.repository, self.extractor), 0)
        self.assertEqual(
            self.repository.session.scalars(select(NewsArticle.article_url)).all(),
            ["/good"],
        )
        self.extractor.side_effect = None
        self.assertEqual(import_player_news(self.repository, self.extractor), 0)
        self.assertEqual(self.extractor.call_count, 3)
        self.assertEqual(
            len(self.repository.session.scalars(select(NewsArticle)).all()), 2
        )

    def test_relative_urls_are_unique_per_base_and_preserve_query_and_fragment(self):
        path = "/en/news/test?edition=en#update"
        urls = [f"https://{host}{path}" for host in ("example.com", "other.com")]
        self.parser.list_news.return_value = [Mock(url=url) for url in urls]
        import_player_news(self.repository, self.extractor)
        articles = self.repository.session.scalars(select(NewsArticle)).all()
        self.assertEqual(len(articles), 2)
        self.assertEqual({article.article_url for article in articles}, {path})
        self.assertEqual(
            {article.base_url for article in articles},
            {"https://example.com", "https://other.com"},
        )
        import_player_news(self.repository, self.extractor)
        self.assertEqual(self.extractor.call_count, 2)
        self.assertEqual(
            self.repository.filter_new_player_news_urls(
                urls + [f"https://third.com{path}"]
            ),
            [f"https://third.com{path}"],
        )

    def test_database_failure_rolls_back_article_and_player_updates(self):
        self.extractor.return_value = ArticlePlayerNews.model_validate(
            {
                "players": [
                    {
                        "info_type": "Transfert",
                        "player_name": "Test",
                        "confirmed": True,
                        "from_team": None,
                        "to_team": "ZSC",
                        "transfer_time": None,
                    }
                ]
            }
        )

        def failed_commit():
            self.repository.session.flush()
            raise IntegrityError("commit", {}, Exception("Database failed"))

        with patch.object(self.repository.session, "commit", side_effect=failed_commit):
            with self.assertLogs(level="ERROR"):
                self.assertEqual(import_player_news(self.repository, self.extractor), 0)
        self.assertEqual(self.repository.session.scalars(select(NewsArticle)).all(), [])
        self.assertEqual(self.repository.session.scalars(select(PlayerNews)).all(), [])
        self.assertEqual(import_player_news(self.repository, self.extractor), 1)
        self.assertEqual(self.extractor.call_count, 2)

    def test_duplicate_filter_uses_articles_without_player_updates(self):
        import_player_news(self.repository, self.extractor)
        self.assertEqual(self.repository.filter_new_player_news_urls([]), [])
        self.assertEqual(
            self.repository.filter_new_player_news_urls(
                ["https://swisshockeynews.ch/en/news/test", "new", "new", "other"]
            ),
            ["new", "new", "other"],
        )


if __name__ == "__main__":
    unittest.main()
