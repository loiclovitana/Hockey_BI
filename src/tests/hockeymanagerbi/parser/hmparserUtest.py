import unittest

from bs4 import BeautifulSoup
from hockeymanagerbi.parser import hmparser


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
        result = hmparser._scrap_player_row(player_row_html)

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
        result = hmparser._scrap_player_details(str(html))

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
        result = hmparser._scrap_players_html_list(html)

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
