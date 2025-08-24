import unittest
from unittest.mock import patch

from hmtracker.loader.playerstats.source import website


class TestPlayerStatsAjaxLoader(unittest.TestCase):
    @patch("hmtracker.parser.hmparser.HMAjaxScrapper.connect_to_hm")
    @patch("hmtracker.parser.hmparser.HMAjaxScrapper.get_all_players")
    @patch("hmtracker.parser.hmparser.HMAjaxScrapper.get_player_stats")
    @patch("hmtracker.parser.hmparser.HMAjaxScrapper.close_session")
    def test_playerstats_ajax_loader(
        self,
        mock_close_session,
        mock_get_player_stats,
        mock_get_all_players,
        mock_connect_to_hm,
    ):
        # Arrange
        mock_get_all_players.return_value = [
            {
                "id": "1",
                "name": "Player1",
                "club": "Club1",
                "role": "Forward",
                "foreigner": "True",
            }
        ]
        mock_get_player_stats.return_value = {
            "Goals": "10",
            "Assists": "5",
            "name": "PlayerName",
        }

        # Act
        data_loader = website.playerstats_ajax_loader("testuser", "testpass")
        data = data_loader()

        # Assert
        mock_connect_to_hm.assert_called_once_with("testuser", "testpass")
        mock_get_all_players.assert_called_once()
        mock_get_player_stats.assert_called_once_with("1")
        mock_close_session.assert_called_once()

        self.assertEqual(1, len(data))
        self.assertIn("Goals", data[0])
        self.assertEqual("10", data[0]["Goals"])
        self.assertIn("name", data[0])
        self.assertEqual("PlayerName", data[0]["name"])


if __name__ == "__main__":
    unittest.main()
