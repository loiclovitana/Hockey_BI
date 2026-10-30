import json
import unittest
from datetime import date, datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, patch

from sqlalchemy import select
from sqlalchemy.orm import Session

from hmtracker.database.database import init_engine
from hmtracker.database.models import (
    HMDatabaseObject,
    HockeyPlayer,
    HockeyPlayerStats,
    NewsArticle,
    NewsPlayerMatch,
    NewsTeamMatch,
    PlayerInfoType,
    PlayerNews,
    Season,
)
from hmtracker.database.repository import RepositorySession
from hmtracker.loader.main import (
    import_playernews_from_shn,
    match_playernews_to_players,
)
from hmtracker.loader.playernews.extractor import ArticlePlayerNews
from hmtracker.loader.playernews.matcher import (
    PlayerSelection,
    TeamSelection,
    match_player_news,
    select_player,
    select_team,
)
from hmtracker.parser.models import ArticleDetails

MATCHER = "hmtracker.loader.playernews.matcher"


class TestPlayerNewsMatcher(unittest.TestCase):
    def setUp(self):
        self.engine = init_engine("sqlite://")
        HMDatabaseObject.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)
        self.session = Session(self.engine, autoflush=False)
        self.repository = RepositorySession(self.session)
        self.addCleanup(self.session.close)
        self.season = Season(
            id=1,
            name="Current",
            start=date.today() - timedelta(days=100),
            end=date.today() + timedelta(days=100),
            arcade=False,
        )
        self.session.add(self.season)
        self.session.commit()
        self.team_llm = self.enterContext(
            patch(f"{MATCHER}.select_team", return_value=None)
        )
        self.player_llm = self.enterContext(
            patch(f"{MATCHER}.select_player", return_value=None)
        )

    def player(self, player_id, name="Müller L.", club="ZSC", season_id=1):
        player = HockeyPlayer(
            id=player_id,
            season_id=season_id,
            name=name,
            role="FW",
            foreigner=False,
        )
        self.session.add(player)
        self.session.flush()
        if club:
            self.stat(player_id, club, season_id=season_id)
        return player

    def stat(self, player_id, club, days_ago=0, season_id=1):
        self.session.add(
            HockeyPlayerStats(
                player_id=player_id,
                season_id=season_id,
                club=club,
                price=1,
                validity_date=datetime.combine(
                    date.today() - timedelta(days=days_ago), datetime.min.time()
                ),
            )
        )
        self.session.flush()

    def news(self, name="Léon Muller", team="Zürich", days_ago=0, **kwargs):
        news = PlayerNews(
            article=NewsArticle(
                base_url="https://example.com",
                article_url=f"https://example.com/{uuid4()}",
                article_date=date.today() - timedelta(days=days_ago),
                title="Player update",
                processed_by="test-model",
            ),
            player_name=name,
            current_team=team,
            confirmed=True,
            info_type=PlayerInfoType.INJURY,
            availability_time=None,
            **kwargs,
        )
        self.session.add(news)
        self.session.flush()
        return news

    def match(self, **kwargs):
        return match_player_news(self.repository, **kwargs)

    def add_old_season(self):
        self.session.add(
            Season(
                id=2,
                name="Old",
                start=date(2000, 1, 1),
                end=date(2001, 1, 1),
                arcade=False,
            )
        )
        self.session.flush()

    def test_no_current_season_skips_before_any_matching(self):
        self.session.delete(self.season)
        self.session.commit()
        self.assertIsNone(self.repository.get_current_season())
        self.assertEqual(self.match(), 0)
        self.team_llm.assert_not_called()
        self.player_llm.assert_not_called()

    def test_arcade_season_is_not_used(self):
        self.season.arcade = True
        self.session.commit()
        self.assertEqual(self.match(), 0)

    def test_no_players_skips_llm(self):
        self.news(team="Unknown club")
        self.assertEqual(self.match(), 0)
        self.team_llm.assert_not_called()

    def test_initial_surname_team_is_case_and_accent_insensitive(self):
        self.player(1)
        self.player(2, "Muller R.")
        self.player(3, "Muller L.", "AJO")
        news = self.news()
        self.assertEqual(self.match(), 1)
        self.assertEqual((news.player_id, news.season_id), (1, 1))
        self.assertEqual(news.current_team, "ZSC")
        self.team_llm.assert_not_called()
        self.player_llm.assert_not_called()

    def test_conflicting_initial_and_team_require_review_of_both_players(self):
        self.player(1)
        self.player(2, "Muller R.", "AJO")
        news = self.news(team="Ajoie")
        self.assertEqual(self.match(), 0)
        self.assertIsNone(news.player_id)
        self.player_llm.assert_called_once()
        self.assertEqual({p.id for p in self.player_llm.call_args.args[1]}, {1, 2})

    def test_single_conflicting_initial_requires_review(self):
        self.player(1, "Muller R.")
        news = self.news()
        self.assertEqual(self.match(), 0)
        self.assertIsNone(news.player_id)
        self.player_llm.assert_called_once()
        self.assertEqual([p.id for p in self.player_llm.call_args.args[1]], [1])

    def test_single_conflicting_team_requires_review(self):
        self.player(1, club="AJO")
        news = self.news()
        self.assertEqual(self.match(), 0)
        self.assertIsNone(news.player_id)
        self.player_llm.assert_called_once()

    def test_transfer_context_can_resolve_a_team_conflict(self):
        self.player(1)
        self.player(2, "Muller R.", "AJO")
        news = self.news(team="Ajoie")
        news.info_type = PlayerInfoType.TRANSFERT
        news.new_team = "Zurich"
        news.article.title = "Leon Muller leaves Ajoie for Zurich"
        self.player_llm.return_value = 1
        self.assertEqual(self.match(), 1)
        self.assertEqual(news.player_id, 1)
        self.assertEqual((news.current_team, news.new_team), ("AJO", "ZSC"))
        self.player_llm.assert_called_once()
        self.assertEqual({p.id for p in self.player_llm.call_args.args[1]}, {1, 2})

    def test_initial_surname_without_team_or_stats(self):
        self.player(1, club=None)
        news = self.news(team=None)
        self.assertEqual(self.match(), 1)
        self.assertEqual(news.player_id, 1)
        self.team_llm.assert_not_called()
        self.player_llm.assert_not_called()

    def test_compound_names_and_initials_before_or_after_surname(self):
        self.player(1, "de la Rose J.")
        self.player(2, "J.-P. Dumont", "AJO")
        first = self.news("Jacob de la Rose")
        second = self.news("Jean-Pierre Dumont", "AJO")
        self.assertEqual(self.match(), 2)
        self.assertEqual([first.player_id, second.player_id], [1, 2])
        self.player_llm.assert_not_called()

    def test_surname_only_with_team(self):
        self.player(1)
        news = self.news("Muller")
        self.assertEqual(self.match(), 1)
        self.assertEqual(news.player_id, 1)

    def test_latest_club_only_in_current_season_and_not_future(self):
        self.player(1, club="AJO")
        self.stat(1, "ZSC", days_ago=1)
        self.stat(1, "ZSC", days_ago=-1)
        self.player(2)
        self.session.add(
            Season(
                id=2,
                name="Old",
                start=date(2000, 1, 1),
                end=date(2001, 1, 1),
            )
        )
        self.session.flush()
        self.player(2, "Muller L.", "AJO", season_id=2)
        news = self.news()
        self.assertEqual(self.match(), 1)
        self.assertEqual(news.player_id, 2)
        self.player_llm.assert_not_called()

    def test_ambiguous_exact_matches_use_llm_and_reuse_saved_decision(self):
        self.player(1)
        self.player(2, "Muller L.")
        first, second = self.news(), self.news()
        self.player_llm.return_value = 2
        self.assertEqual(self.match(), 2)
        self.assertEqual([first.player_id, second.player_id], [2, 2])
        self.player_llm.assert_called_once()
        self.assertEqual({p.id for p in self.player_llm.call_args.args[1]}, {1, 2})
        self.assertEqual(self.player_llm.call_args.kwargs["team_code"], "ZSC")
        self.assertEqual(
            self.session.get(NewsPlayerMatch, ("leon muller", "ZSC", 1)).player_id, 2
        )
        self.session.commit()
        third = self.news()
        self.assertEqual(self.match(), 1)
        self.assertEqual(third.player_id, 2)
        self.player_llm.assert_called_once()

    def test_different_team_aliases_reuse_player_decision_by_code(self):
        self.player(1)
        self.player(2)
        first = self.news(team="Zurich")
        second = self.news(team="ZSC Lions")
        self.player_llm.return_value = 2
        self.assertEqual(self.match(), 2)
        self.assertEqual([first.player_id, second.player_id], [2, 2])
        self.player_llm.assert_called_once()
        saved = self.session.scalars(select(NewsPlayerMatch)).one()
        self.assertEqual(saved.team_code, "ZSC")

    def test_unresolved_team_decision_is_not_cached(self):
        self.player(1)
        self.news("Leon Mullre", team="Foreign club")
        self.player_llm.return_value = 1
        self.assertEqual(self.match(), 1)
        self.assertIsNone(self.player_llm.call_args.kwargs["team_code"])
        self.assertEqual(self.session.scalars(select(NewsPlayerMatch)).all(), [])

    def test_unresolved_teams_do_not_share_decisions_or_reuse_legacy_empty_key(self):
        self.player(1)
        self.player(2, club="AJO")
        self.session.add(
            NewsPlayerMatch(
                player_name="leon mullre", team_code="", season_id=1, player_id=1
            )
        )
        self.session.flush()
        first = self.news("Leon Mullre", team="Foreign club A")
        second = self.news("Leon Mullre", team="Foreign club B")
        self.player_llm.side_effect = [1, 2]
        self.assertEqual(self.match(), 2)
        self.assertEqual([first.player_id, second.player_id], [1, 2])
        self.assertEqual(self.player_llm.call_count, 2)

    def test_missing_team_does_not_reuse_an_unresolved_team_decision(self):
        self.player(1)
        self.session.add(
            NewsPlayerMatch(
                player_name="leon mullre", team_code="", season_id=1, player_id=1
            )
        )
        self.session.flush()
        news = self.news("Leon Mullre", team=None)
        self.assertEqual(self.match(), 0)
        self.assertIsNone(news.player_id)
        self.player_llm.assert_called_once()

    def test_more_than_two_exact_matches_are_all_sent_to_llm(self):
        for player_id in range(1, 5):
            self.player(player_id)
        self.news()
        self.assertEqual(self.match(), 0)
        self.assertEqual(len(self.player_llm.call_args.args[1]), 4)

    def test_typo_shortlists_five_current_season_players(self):
        self.player(1)
        for player_id in range(2, 8):
            self.player(player_id, f"Other{player_id} X.", "AJO")
        news = self.news("Leon Mullre")
        self.player_llm.return_value = 1
        self.assertEqual(self.match(), 1)
        shortlist = self.player_llm.call_args.args[1]
        self.assertEqual(len(shortlist), 5)
        self.assertEqual(shortlist[0].id, 1)
        self.assertEqual(news.player_id, 1)

    def test_llm_can_decline_all_similar_players(self):
        self.player(1)
        news = self.news("Completely Different")
        self.assertEqual(self.match(), 0)
        self.assertIsNone(news.player_id)
        self.assertIsNone(news.season_id)
        self.assertEqual(self.session.scalars(select(NewsPlayerMatch)).all(), [])

    def test_team_llm_alias_is_saved_and_reused(self):
        self.player(1)
        self.player(2, "Muller L.", "AJO")
        first = self.news(team="The city lions")
        second = self.news(team="THE CITY LIONS")
        self.team_llm.return_value = "ZSC"
        self.assertEqual(self.match(), 2)
        self.assertEqual([first.player_id, second.player_id], [1, 1])
        self.assertEqual([first.current_team, second.current_team], ["ZSC", "ZSC"])
        self.team_llm.assert_called_once()
        self.assertEqual(
            self.session.get(NewsTeamMatch, "the city lions").team_code, "ZSC"
        )
        self.player_llm.assert_not_called()

    def test_unmatched_team_can_still_match_initial_and_surname(self):
        self.player(1)
        news = self.news(team="Foreign club")
        self.assertEqual(self.match(), 1)
        self.assertEqual(news.player_id, 1)
        self.assertEqual(news.current_team, "Foreign club")
        self.assertEqual(self.session.scalars(select(NewsTeamMatch)).all(), [])

    def test_transfer_uses_destination_when_origin_is_unknown(self):
        self.player(1)
        news = PlayerNews(
            article=NewsArticle(
                base_url="https://example.com",
                article_url="https://example.com/transfer",
                article_date=date.today(),
                title="Transfer",
                processed_by="test-model",
            ),
            player_name="Leon Muller",
            current_team=None,
            new_team="Zurich",
            info_type=PlayerInfoType.TRANSFERT,
            confirmed=True,
            availability_time="Tomorrow",
        )
        self.session.add(news)
        self.session.flush()
        self.assertEqual(self.match(), 1)
        self.assertEqual(news.player_id, 1)
        self.assertEqual((news.current_team, news.new_team), (None, "ZSC"))

    def test_since_d_and_replace_filter_records(self):
        self.player(1)
        boundary = self.news(days_ago=30)
        older = self.news(days_ago=31)
        future = self.news(days_ago=-1)
        linked = self.news(player_id=1, season_id=1)
        self.assertEqual(self.match(), 1)
        self.assertEqual(boundary.player_id, 1)
        self.assertIsNone(older.player_id)
        self.assertIsNone(future.player_id)
        self.assertEqual(self.match(since_d=0, replace=True), 1)
        self.assertEqual(linked.player_id, 1)
        self.assertEqual(self.match(since_d=31), 1)
        self.assertEqual(older.player_id, 1)

    def test_replace_rechecks_existing_link_and_saved_player_decision(self):
        self.player(1)
        self.player(2)
        news = self.news(player_id=1, season_id=1)
        second = self.news(player_id=1, season_id=1)
        self.session.add(
            NewsPlayerMatch(
                player_name="leon muller",
                team_code="ZSC",
                season_id=1,
                player_id=1,
            )
        )
        self.session.flush()
        self.assertEqual(self.match(), 0)
        self.player_llm.side_effect = [2, 1]
        self.assertEqual(self.match(replace=True), 2)
        self.assertEqual([news.player_id, second.player_id], [2, 2])
        self.player_llm.assert_called_once()
        self.assertEqual(
            self.session.get(NewsPlayerMatch, ("leon muller", "ZSC", 1)).player_id, 2
        )

    def test_replace_reuses_decision_first_learned_during_this_run(self):
        self.player(1)
        self.player(2)
        first, second = self.news(), self.news()
        self.player_llm.side_effect = [2, 1]
        self.assertEqual(self.match(replace=True), 2)
        self.assertEqual([first.player_id, second.player_id], [2, 2])
        self.player_llm.assert_called_once()
        self.session.commit()
        third = self.news()
        self.assertEqual(self.match(), 1)
        self.assertEqual(third.player_id, 2)
        self.player_llm.assert_called_once()

    def test_replace_with_no_match_preserves_existing_link(self):
        self.player(1)
        news = self.news("Other Person", player_id=1, season_id=1)
        self.assertEqual(self.match(replace=True), 0)
        self.assertEqual((news.player_id, news.season_id), (1, 1))

    def test_default_run_rematches_old_season_link_with_reused_player_id(self):
        self.add_old_season()
        current_player = self.player(1)
        old_player = self.player(1, season_id=2)
        news = self.news(player_id=1, season_id=2)
        self.assertIs(news.player, old_player)
        self.assertEqual(self.match(), 1)
        self.assertEqual((news.player_id, news.season_id), (1, 1))
        self.assertIs(news.player, current_player)
        self.player_llm.assert_not_called()

    def test_unmatched_old_links_are_cleared_with_or_without_replace(self):
        self.add_old_season()
        self.player(1)
        old_player = self.player(99, "Other Person", season_id=2)
        for replace in (False, True):
            with self.subTest(replace=replace):
                news = self.news("Other Person", player_id=99, season_id=2)
                self.assertIs(news.player, old_player)
                self.assertEqual(self.match(replace=replace), 0)
                self.assertEqual((news.player_id, news.season_id), (None, None))
                self.assertIsNone(news.player)

    def test_old_link_is_cleared_when_current_roster_is_empty(self):
        self.add_old_season()
        self.player(99, season_id=2)
        news = self.news(player_id=99, season_id=2)
        self.assertEqual(self.match(), 0)
        self.assertEqual((news.player_id, news.season_id), (None, None))
        self.team_llm.assert_not_called()
        self.player_llm.assert_not_called()

    def test_old_links_outside_lookback_are_preserved(self):
        self.add_old_season()
        self.player(1)
        self.player(99, season_id=2)
        news = self.news(days_ago=31, player_id=99, season_id=2)
        self.assertEqual(self.match(replace=True), 0)
        self.assertEqual((news.player_id, news.season_id), (99, 2))

    def test_old_season_cache_is_ignored(self):
        self.add_old_season()
        self.player(1)
        self.player(99, season_id=2)
        self.session.add(
            NewsPlayerMatch(
                player_name="leon mullre", team_code="ZSC", season_id=2, player_id=99
            )
        )
        self.session.flush()
        news = self.news("Leon Mullre")
        self.player_llm.return_value = 1
        self.assertEqual(self.match(), 1)
        self.assertEqual((news.player_id, news.season_id), (1, 1))
        self.assertEqual(
            [(p.id, p.season_id) for p in self.player_llm.call_args.args[1]], [(1, 1)]
        )

    def test_legacy_cache_pointing_outside_current_roster_is_deleted_and_retried(self):
        self.add_old_season()
        self.player(1)
        self.player(99, season_id=2)
        news = self.news("Leon Mullre")
        self.session.commit()
        # Simulate invalid data written before application FK enforcement.
        self.session.connection().exec_driver_sql("PRAGMA foreign_keys=OFF")
        self.session.add(
            NewsPlayerMatch(
                player_name="leon mullre", team_code="ZSC", season_id=1, player_id=99
            )
        )
        self.session.commit()
        self.session.connection().exec_driver_sql("PRAGMA foreign_keys=ON")
        self.assertEqual(self.match(), 0)
        self.assertEqual((news.player_id, news.season_id), (None, None))
        self.assertIsNone(self.session.get(NewsPlayerMatch, ("leon mullre", "ZSC", 1)))
        self.player_llm.assert_called_once()
        self.assertEqual([p.id for p in self.player_llm.call_args.args[1]], [1])
        self.player_llm.return_value = 1
        self.assertEqual(self.match(), 1)
        self.assertEqual((news.player_id, news.season_id), (1, 1))
        self.assertEqual(
            self.session.get(NewsPlayerMatch, ("leon mullre", "ZSC", 1)).player_id, 1
        )

    def test_invalid_lookback_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "since_d"):
            self.match(since_d=-1)

    def test_loader_wrapper_commits_links(self):
        self.player(1)
        news = self.news()
        self.session.commit()
        self.assertEqual(match_playernews_to_players(self.repository), 1)
        with Session(self.engine) as session:
            self.assertEqual(session.get(PlayerNews, news.id).player_id, 1)
            self.assertEqual(session.get(PlayerNews, news.id).current_team, "ZSC")

    def test_loader_wrapper_rolls_back_on_llm_failure(self):
        self.player(1)
        first = self.news()
        self.news("Other Person")
        self.session.commit()
        self.player_llm.side_effect = RuntimeError("LLM unavailable")
        with self.assertRaisesRegex(RuntimeError, "LLM unavailable"):
            match_playernews_to_players(self.repository)
        self.assertIsNone(first.player_id)

    def import_news(self):
        parser = self.enterContext(
            patch("hmtracker.loader.playernews.importer.SwissHockeyNewsParser")
        ).return_value
        parser.list_news.return_value = [Mock(url="https://example.com/new-news")]
        parser.article_details.return_value = ArticleDetails(
            date=date.today(),
            title="Player update",
            description="News",
            text="Léon Muller is injured.",
        )
        agent = self.enterContext(
            patch("hmtracker.loader.playernews.extractor._create_agent")
        ).return_value
        agent.run_sync.return_value.output = ArticlePlayerNews.model_validate(
            {
                "players": [
                    {
                        "info_type": "Absence",
                        "player_name": "Léon Muller",
                        "team": "Zürich",
                        "reason": "Injury",
                        "confirmed": True,
                        "is_return": False,
                        "expected_duration_or_return": None,
                    }
                ]
            }
        )
        return import_playernews_from_shn(self.repository)

    def test_import_loader_matches_and_commits_new_and_existing_news(self):
        self.player(1)
        self.news()
        self.assertEqual(self.import_news(), 1)
        with Session(self.engine) as session:
            news = session.scalars(select(PlayerNews)).all()
            self.assertEqual(len(news), 2)
            self.assertEqual(
                [(item.player_id, item.season_id) for item in news], [(1, 1)] * 2
            )

    def test_import_loader_preserves_imported_news_on_matching_failure(self):
        self.player(1)
        self.player(2)
        self.player_llm.side_effect = RuntimeError("LLM unavailable")
        with self.assertRaisesRegex(RuntimeError, "LLM unavailable"):
            self.import_news()
        with Session(self.engine) as session:
            news = session.scalars(select(PlayerNews)).one()
            self.assertIsNone(news.player_id)


class TestMatchingLlmSelections(unittest.TestCase):
    @patch(f"{MATCHER}.create_news_agent")
    def test_team_selection_rejects_invented_codes(self, factory):
        factory.return_value.run_sync.return_value.output = TeamSelection(
            team_code="INVALID"
        )
        with self.assertRaisesRegex(ValueError, "unknown team code"):
            select_team("Zurich", {"ZSC", "AJO"})

    @patch(f"{MATCHER}.create_news_agent")
    def test_player_selection_rejects_ids_outside_candidates(self, factory):
        news = PlayerNews(
            player_name="Test",
            article=NewsArticle(title="News", article_date=date.today()),
            info_type=PlayerInfoType.INJURY,
        )
        candidates = [HockeyPlayer(id=1, name="Test P.", season_id=1)]
        factory.return_value.run_sync.return_value.output = PlayerSelection(
            player_id=999
        )
        with self.assertRaisesRegex(ValueError, "outside the candidates"):
            select_player(news, candidates, {}, team_code="ZSC")

    @patch(f"{MATCHER}.create_news_agent")
    def test_player_prompt_includes_news_context_and_allows_no_match(self, factory):
        news = PlayerNews(
            player_name="Test",
            article=NewsArticle(title="News", article_date=date.today()),
            info_type=PlayerInfoType.TRANSFERT,
            current_team="Zurich",
            new_team="Ajoie",
            availability_time="Next season",
        )
        factory.return_value.run_sync.return_value.output = PlayerSelection(
            player_id=None
        )
        self.assertIsNone(
            select_player(
                news, [HockeyPlayer(id=1, name="Test P.")], {1: "ZSC"}, team_code="ZSC"
            )
        )
        prompt = json.loads(factory.return_value.run_sync.call_args.args[0])
        self.assertEqual(prompt["news"]["team_code"], "ZSC")
        self.assertEqual(prompt["news"]["current_team"], "Zurich")
        self.assertEqual(prompt["news"]["new_team"], "Ajoie")
        self.assertEqual(prompt["news"]["availability_time"], "Next season")
        self.assertEqual(
            prompt["candidates"], [{"id": 1, "name": "Test P.", "team_code": "ZSC"}]
        )


class TestMatchingTask(unittest.TestCase):
    def test_background_task_forwards_arguments_and_registers_history(self):
        from hmtracker.services import admin

        with (
            patch.dict("os.environ", {"HM_DATABASE_URL": "sqlite://"}),
            patch.object(admin, "_current_operation", None),
            patch.object(admin, "Thread") as thread,
            patch.object(admin, "registerTask") as register,
            patch.object(admin.loader, "match_playernews_to_players") as match,
        ):
            thread.return_value.start.side_effect = lambda: thread.call_args.kwargs[
                "target"
            ]()
            admin.start_matching_playernews(since_d=7, replace=True)
            match.assert_called_once_with("sqlite://", 7, True)
            self.assertEqual(register.call_args.args[0].name, "Match player news")
            self.assertIsNone(register.call_args.args[0].error)
