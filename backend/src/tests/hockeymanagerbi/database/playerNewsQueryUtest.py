import os
import unittest
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from hmtracker.database.database import init_engine
from hmtracker.database.models import (
    HMDatabaseObject,
    HockeyPlayer,
    NewsArticle,
    PlayerInfoType,
    PlayerNews,
    Season,
)
from hmtracker.database.repository import RepositorySession


class TestPlayerNewsFilters(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"HM_DATABASE_URL": "sqlite://"}):
            from hmtracker.api.routers.players import get_session, router

        directory = self.enterContext(TemporaryDirectory())
        self.engine = init_engine(f"sqlite:///{Path(directory) / 'news.sqlite'}")
        self.addCleanup(self.engine.dispose)
        HMDatabaseObject.metadata.create_all(self.engine)
        today = date.today()
        with Session(self.engine) as session:
            session.add(Season(id=1, name="Test", start=today, end=today))
            session.flush()
            session.add_all(
                HockeyPlayer(
                    id=player_id,
                    season_id=1,
                    name=f"Player {player_id}",
                    role="FW",
                    foreigner=False,
                )
                for player_id in (7, 8, 9)
            )
            session.flush()
            for news_id, player_id, days_ago in (
                (1, 7, 31),
                (2, 7, 30),
                (3, 8, 5),
                (4, 9, 1),
                (5, 7, 0),
                (6, 8, -1),
                (7, None, 2),
            ):
                session.add(
                    PlayerNews(
                        id=news_id,
                        player_id=player_id,
                        season_id=1 if player_id is not None else None,
                        player_name=f"Player {player_id}",
                        info_type=PlayerInfoType.INJURY,
                        article=NewsArticle(
                            base_url="https://example.com",
                            article_url=f"/news/{news_id}",
                            article_date=today - timedelta(days=days_ago),
                            title=f"News {news_id}",
                        ),
                    )
                )
            session.commit()

        def override_session():
            with RepositorySession(Session(self.engine)) as repository:
                yield repository

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_session] = override_session
        self.client = self.enterContext(TestClient(app))

    def test_combines_player_list_with_time_limit_before_pagination(self):
        response = self.client.get(
            "/players/news",
            params={"player_ids": [7, 8], "time_limit": 30, "season_id": 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], [5, 3, 2])
        self.assertEqual(response.json()[0]["article"]["title"], "News 5")
        response = self.client.get(
            "/players/news",
            params={"player_ids": [7, 8], "time_limit": 30, "limit": 1, "offset": 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], [3])

    def test_optional_filters_and_today_only(self):
        for params, expected in (
            ({}, [6, 5, 4, 7, 3, 2, 1]),
            ({"player_ids": [7]}, [5, 2, 1]),
            ({"player_ids": [7, 8, 7]}, [6, 5, 3, 2, 1]),
            ({"player_ids": [99]}, []),
            ({"time_limit": 30}, [5, 4, 7, 3, 2]),
            ({"time_limit": 0}, [5]),
        ):
            with self.subTest(params=params):
                response = self.client.get("/players/news", params=params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.headers["cache-control"], "public, max-age=14400"
                )
                self.assertEqual([item["id"] for item in response.json()], expected)

    def test_rejects_invalid_filters(self):
        for params in (
            {"player_ids": [7, "invalid"]},
            {"time_limit": -1},
            {"time_limit": "invalid"},
        ):
            with self.subTest(params=params):
                response = self.client.get("/players/news", params=params)
                self.assertEqual(response.status_code, 422)
                self.assertNotIn("cache-control", response.headers)

    def test_empty_player_list_matches_no_players(self):
        with RepositorySession(Session(self.engine)) as repository:
            self.assertEqual(repository.get_player_news(player_ids=[]), [])
