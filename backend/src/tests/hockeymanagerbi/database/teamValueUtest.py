import unittest
from datetime import date, datetime
from unittest.mock import patch

from sqlalchemy.orm import Session

from hmtracker.database.database import init_engine
from hmtracker.database.models import (
    HMDatabaseObject,
    HockeyPlayer,
    HockeyPlayerStats,
    Manager,
    Match,
    Season,
    Team,
)
from hmtracker.database.repository import RepositorySession
from hmtracker.services.team_value import TeamModification, compute_team_value_sql


class TestTeamValue(unittest.TestCase):
    def setUp(self):
        engine = init_engine("sqlite://")
        self.addCleanup(engine.dispose)
        HMDatabaseObject.metadata.create_all(engine)
        self.repository = self.enterContext(RepositorySession(Session(engine)))
        session = self.repository.session
        session.add_all(
            [
                Season(id=1, name="Test", start=date(2026, 8, 1), end=date(2027, 7, 1)),
                Season(
                    id=2, name="Other", start=date(2025, 8, 1), end=date(2026, 7, 1)
                ),
                Manager(id=1),
                Match(
                    home_club="A", away_club="B", match_datetime=datetime(2026, 10, 1)
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                HockeyPlayer(
                    id=1, season_id=1, name="Skater", role="FW", foreigner=False
                ),
                HockeyPlayer(
                    id=2, season_id=1, name="Goalkeeper", role="GK", foreigner=False
                ),
                # The same ID in another season must neither duplicate nor change the role.
                HockeyPlayer(
                    id=1, season_id=2, name="Other", role="GK", foreigner=False
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                Team(id=1, team="test", manager_id=1, player_id=1, season_id=1),
                Team(id=2, team="test", manager_id=1, player_id=2, season_id=1),
            ]
        )
        for player_id, price, points, appearances in [(1, 10, 25, 2), (2, 9, 44, 17)]:
            session.add(
                HockeyPlayerStats(
                    player_id=player_id,
                    season_id=1,
                    validity_date=datetime(2026, 9, 30),
                    club="A",
                    price=price,
                    hm_points=points,
                    appearances=appearances,
                )
            )
        session.add(
            HockeyPlayerStats(
                player_id=1,
                season_id=1,
                validity_date=datetime(2026, 10, 2),
                club="A",
                price=11,
                hm_points=40,
                appearances=3,
            )
        )
        session.commit()

    def compute(self, modifications=None):
        with (
            patch("hmtracker.services.team_value.datetime") as clock,
            patch.object(
                self.repository.session,
                "execute",
                wraps=self.repository.session.execute,
            ) as execute,
        ):
            clock.now.return_value = datetime(2026, 10, 3)
            result = compute_team_value_sql(
                self.repository, 1, 1, "test", modifications
            )
            self.assertEqual(execute.call_count, 1)
        return result

    def test_preserves_fractional_averages_and_goalkeeper_prices_over_time(self):
        historical, current = self.compute()
        self.assertEqual(historical.at, datetime(2026, 10, 1))
        self.assertEqual(historical.value, 19)
        self.assertEqual(historical.theorical_value, 21.5)
        self.assertEqual(current.value, 20)
        self.assertAlmostEqual(current.theorical_value, 40 / 3 + 9)

    def test_missing_or_zero_appearances_and_missing_points_fall_back_to_price(self):
        stats = self.repository.session.get(
            HockeyPlayerStats, (1, 1, datetime(2026, 10, 2))
        )
        for points, appearances in [(40, None), (40, 0), (None, 3)]:
            with self.subTest(points=points, appearances=appearances):
                stats.hm_points = points
                stats.appearances = appearances
                self.repository.session.flush()
                self.assertEqual(self.compute()[-1].theorical_value, 20)

    def test_modifications_use_replacement_player_role(self):
        self.repository.session.delete(self.repository.session.get(Team, 2))
        self.repository.session.flush()
        results = self.compute([TeamModification(team_id=1, replaced_player_id=2)])
        for result in results:
            self.assertEqual(result.value, 9)
            self.assertEqual(result.theorical_value, 9)
