import datetime
import unittest
from unittest.mock import MagicMock, patch

import hmtracker.loader.playerstats.mapper as mapper


class TestPlayerStatsConverter(unittest.TestCase):
    correct_data = [
        {"id": "13", "date": "2020-12-30", "Ownership": "2.9%", "foreigner": "true"},
        {"id": "1", "date": "2020-01-01", "Ownership": "4", "foreigner": "Oui"},
    ]

    def test_existing_fields(self):
        self.assertIn("id", mapper.FIELDS)
        self.assertIn("date", mapper.FIELDS)
        self.assertIn("Ownership", mapper.FIELDS)
        self.assertIn("foreigner", mapper.FIELDS)
        self.assertNotIn("invalid field", mapper.FIELDS)

    def test_convert_data(self):
        result = mapper._convert_data(self.correct_data)

        self.assertEqual(2, len(result))

        self.assertEqual(13, result[0]["id"])
        self.assertEqual(datetime.date(2020, 12, 30), result[0]["date"])
        self.assertAlmostEqual(2.9, result[0]["Ownership"])
        self.assertEqual(True, result[0]["foreigner"])

        self.assertEqual(1, result[1]["id"])
        self.assertEqual(datetime.date(2020, 1, 1), result[1]["date"])
        self.assertAlmostEqual(4, result[1]["Ownership"])
        self.assertEqual(True, result[1]["foreigner"])

    def test_convert_not_existing_data(self):
        result = mapper._convert_data([{"invalid field": "useless"}])

        self.assertEqual(1, len(result))
        self.assertNotIn("invalid field", result[0])
        self.assertIsNone(result[0]["id"])
        self.assertIsNone(result[0]["date"])
        self.assertIsNone(result[0]["Ownership"])
        self.assertIsNone(result[0]["foreigner"])

    def test_convert_invalid_data(self):
        result = mapper._convert_data(
            [{"id": "Id:12", "date": "today", "Ownership": "non", "foreigner": "very"}]
        )

        self.assertEqual(1, len(result))
        self.assertIn("id", result[0])
        self.assertIsNone(result[0]["id"])
        self.assertIsNone(result[0]["date"])
        self.assertIsNone(result[0]["Ownership"])
        self.assertIsNone(result[0]["foreigner"])

    def test_map_player_stats(self):
        players, players_stats = mapper.map_player_stats(self.correct_data)

        self.assertEqual(2, len(players))
        self.assertEqual(2, len(players_stats))

        self.assertEqual(13, players[0].id)
        self.assertEqual(True, players[0].foreigner)
        self.assertIsNone(players[0].role)

        self.assertEqual(13, players_stats[0].player_id)
        self.assertEqual(datetime.date(2020, 12, 30), players_stats[0].validity_date)
        self.assertEqual(2.9, players_stats[0].ownership)
        self.assertIsNone(players_stats[0].goal)


class TestMapPlayerStats(unittest.TestCase):
    @patch("hmtracker.database.models.HockeyPlayer")
    @patch("hmtracker.database.models.HockeyPlayerStats")
    def test_map_player_stats(self, mock_HockeyPlayerStats, mock_HockeyPlayer):
        # Arrange: mock data for player stats
        player_stats_data = [
            {
                "id": "1",
                "name": "Player One",
                "club": "Club A",
                "role": "Forward",
                "foreigner": "YES",
                "date": "2023-10-01",
                "Price": "15.5",
                "Ownership": "23.5%",
                "HM points": "56.7",
                "Appareances": "20",
                "Goal": "10",
                "Goal OT": "2",
                "Assist #1": "5",
                "Assist #2": "3",
                "Assist OT": "1",
                "Points": "19",
                "GWG": "2",
                "Penalties": "15",
                "+/-": "10",
                "Shots": "100",
            }
        ]

        # Expected converted data for player and player stats
        mock_HockeyPlayer.return_value = MagicMock()
        mock_HockeyPlayerStats.return_value = MagicMock()

        # Act
        players, players_stats = mapper.map_player_stats(player_stats_data)

        # Assert: validate that both player and player stats were created with correct arguments
        mock_HockeyPlayer.assert_called_once_with(
            id=1, name="Player One", role="Forward", foreigner=True
        )
        mock_HockeyPlayerStats.assert_called_once_with(
            player_id=1,
            validity_date=datetime.date(2023, 10, 1),
            price=15.5,
            club="Club A",
            hm_points=56.7,
            appearances=20,
            ownership=23.5,
            goal=10,
            assists=9,  # Assist #1 + Assist #2 + Assist OT
            penalties=15,
            plus_minus=10,
        )

    @patch("hmtracker.database.models.HockeyPlayer")
    @patch("hmtracker.database.models.HockeyPlayerStats")
    def test_map_player_stats_with_missing_values(
        self, mock_HockeyPlayerStats, mock_HockeyPlayer
    ):
        # Arrange: simulate player stats data with missing fields
        player_stats_data = [
            {
                "id": "2",
                "name": "Player Two",
                "club": "Club B",
                "role": "Goalie",
                "foreigner": "",
                "date": "",
                "Price": "",
                "Ownership": "12.5%",
                "HM points": "40",
                "Appareances": "18",
                "Goal": "",
                "Assist #1": "",
                "Assist #2": "",
                "Assist OT": "",
                "Penalties": "10",
                "+/-": "5",
            }
        ]

        mock_HockeyPlayer.return_value = MagicMock()
        mock_HockeyPlayerStats.return_value = MagicMock()

        # Act
        players, players_stats = mapper.map_player_stats(player_stats_data)

        # Assert: check correct handling of missing values
        mock_HockeyPlayer.assert_called_once_with(
            id=2, name="Player Two", role="Goalie", foreigner=None
        )
        mock_HockeyPlayerStats.assert_called_once_with(
            player_id=2,
            validity_date=None,  # Missing date should be None
            price=None,  # Missing price should be None
            hm_points=40.0,
            appearances=18,
            club="Club B",
            ownership=12.5,
            goal=None,  # Missing goal should be None
            assists=None,  # Missing assists should be None
            penalties=10,
            plus_minus=5,
        )

    @patch("hmtracker.database.models.HockeyPlayer")
    @patch("hmtracker.database.models.HockeyPlayerStats")
    def test_map_player_stats_with_invalid_values(
        self, mock_HockeyPlayerStats, mock_HockeyPlayer
    ):
        # Arrange: simulate invalid data that should trigger warnings
        player_stats_data = [
            {
                "id": "abc",  # Invalid id
                "name": "Player Three",
                "club": "Club C",
                "role": "Forward",
                "foreigner": "UNKNOWN",  # Invalid boolean conversion
                "date": "invalid-date",  # Invalid date
                "Price": "invalid-price",  # Invalid float conversion
                "Ownership": "100%",  # Valid percentage float conversion
                "HM points": "100",
                "Appareances": "22",
                "Goal": "12",
                "Assist #1": "4",
                "Assist #2": "2",
                "Assist OT": "1",
                "Penalties": "20",
                "+/-": "8",
            }
        ]

        mock_HockeyPlayer.return_value = MagicMock()
        mock_HockeyPlayerStats.return_value = MagicMock()

        # Act
        players, players_stats = mapper.map_player_stats(player_stats_data)

        # Assert: Ensure the invalid fields are handled properly
        mock_HockeyPlayer.assert_called_once_with(
            id=None,  # Invalid id should be None
            name="Player Three",
            role="Forward",
            foreigner=None,
        )
        mock_HockeyPlayerStats.assert_called_once_with(
            player_id=None,  # Invalid id
            validity_date=None,  # Invalid date
            price=None,  # Invalid price should be None
            hm_points=100.0,
            appearances=22,
            club="Club C",
            ownership=100.0,  # Valid ownership conversion
            goal=12,
            assists=7,  # Assist #1 + Assist #2 + Assist OT
            penalties=20,
            plus_minus=8,
        )


if __name__ == "__main__":
    unittest.main()
