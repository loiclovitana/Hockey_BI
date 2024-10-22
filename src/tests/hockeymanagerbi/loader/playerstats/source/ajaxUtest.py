import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from hockeymanagerbi.loader.playerstats.source import ajax


class TestPlayerStatsAjaxLoader(unittest.TestCase):

    @patch('hockeymanagerbi.loader.playerstats.source.ajax.HMAjaxScrapper.connect_to_hm')
    @patch('hockeymanagerbi.loader.playerstats.source.ajax.HMAjaxScrapper.get_players')
    @patch('hockeymanagerbi.loader.playerstats.source.ajax.HMAjaxScrapper.get_player_stats')
    @patch('hockeymanagerbi.loader.playerstats.source.ajax.HMAjaxScrapper.close_session')
    def test_playerstats_ajax_loader(self, mock_close_session, mock_get_player_stats, mock_get_players,
                                     mock_connect_to_hm):
        # Arrange
        mock_get_players.return_value = [
            {'id': '1', 'name': 'Player1', 'club': 'Club1', 'role': 'Forward', 'foreigner': 'True'}]
        mock_get_player_stats.return_value = {'Goals': '10', 'Assists': '5', 'name': 'PlayerName'}

        # Act
        data_loader = ajax.playerstats_ajax_loader("testuser", "testpass")
        data = data_loader()

        # Assert
        mock_connect_to_hm.assert_called_once_with("testuser", "testpass")
        mock_get_players.assert_called_once()
        mock_get_player_stats.assert_called_once_with('1')
        mock_close_session.assert_called_once()

        self.assertEqual(1, len(data))
        self.assertIn('Goals', data[0])
        self.assertEqual('10', data[0]['Goals'])
        self.assertIn('name', data[0])
        self.assertEqual('PlayerName', data[0]['name'])


class TestScrappingFunctions(unittest.TestCase):

    def test_scrap_player_row(self):
        # Arrange
        html = """
        <div class="row" attr="1">
            <span class="name">Player 1</span>
            <img src="/clubs/Club1/"/>
            <div>Forward</div>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        player_row_html = soup.select_one('.row')

        # Act
        result = ajax._scrap_player_row(player_row_html)

        # Assert
        self.assertEqual('1', result['id'])
        self.assertEqual('Player 1', result['name'])
        self.assertEqual('Club1', result['club'])
        self.assertEqual('Forward', result['role'])
        self.assertEqual('False', result['foreigner'])

    def test_scrap_player_details(self):
        # Arrange
        html = """
        <div class='histogram horiz' label='Goals' value='10'></div>
        <div class='histogram horiz' label='Assists' value='5'></div>
        """

        # Act
        result = ajax._scrap_player_details(str(html))

        # Assert
        self.assertEqual('10', result['Goals'])
        self.assertEqual('5', result['Assists'])

    def test_scrap_players_html_list(self):
        html = """
                <div class="row" attr="1">
                    <span class="name">Player 1</span>
                    <img src="/clubs/Club1/"/>
                    <div>FW</div>
                </div>
                <div class="row" attr="2">
                    <span class="name">Player 2</span>
                    <img src="/clubs/Club2/"/>
                    <i class="flag ch"></i>
                    <div>DF</div>
                </div>
                """
        result = ajax._scrap_players_html_list(html)

        self.assertEqual(2, len(result))

        self.assertEqual("1", result[0]['id'])
        self.assertEqual("Player 1", result[0]['name'])
        self.assertEqual("Club1", result[0]['club'])
        self.assertEqual("FW", result[0]['role'])
        self.assertEqual("False", result[0]['foreigner'])

        self.assertEqual("2", result[1]['id'])
        self.assertEqual("Player 2", result[1]['name'])
        self.assertEqual("Club2", result[1]['club'])
        self.assertEqual("DF", result[1]['role'])
        self.assertEqual("True", result[1]['foreigner'])


if __name__ == '__main__':
    unittest.main()
