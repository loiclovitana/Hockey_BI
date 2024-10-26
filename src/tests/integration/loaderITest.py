import datetime
import unittest
import os
import shutil

from sqlalchemy import create_engine

from hockeymanagerbi.database.creation import initialize_database
from hockeymanagerbi.database.repository import create_repository_session_maker
from hockeymanagerbi.loader.constants import HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME
from hockeymanagerbi.loader.main import import_playerstats_from_csv, import_playerstats_from_loader
from hockeymanagerbi.loader.playerstats.source.ajax import HMAjaxScrapper

TEMP_FOLDER = "tmp"
SQLITE_DB_NAME = "i_test.db"
SQLITE_DB = f"sqlite:///./{TEMP_FOLDER}/{SQLITE_DB_NAME}"


class DatabaseTest(unittest.TestCase):
    session_maker = None

    @classmethod
    def setUpClass(cls):
        if os.path.exists(TEMP_FOLDER):
            raise FileExistsError(f"'{TEMP_FOLDER}' already exists aborting test to avoid unwanted deletion")
        os.mkdir(TEMP_FOLDER)

        initialize_database(SQLITE_DB)

    def setUp(self) -> None:
        self.session_maker = create_repository_session_maker(SQLITE_DB)

    # @classmethod
    # def tearDownClass(cls):
    #      os.remove(f"{TEMP_FOLDER}/{SQLITE_DB_NAME}")

    def test_db_creation(self):
        self.assertTrue(os.path.exists(f"{TEMP_FOLDER}/{SQLITE_DB_NAME}"))

    def test_season_init(self):
        session = self.session_maker()
        season = session.get_current_season()
        self.assertIsNotNone(season)
        self.assertFalse(season.arcade)
        self.assertTrue(datetime.date.today() <= season.end)
        self.assertTrue(datetime.date.today() >= season.start)

        arcade_season = session.get_current_season(arcade=True)
        self.assertIsNotNone(arcade_season)
        self.assertTrue(arcade_season.arcade)
        self.assertTrue(datetime.date.today() <= arcade_season.end)
        self.assertTrue(datetime.date.today() >= arcade_season.start)

        session.end_session()

    def test_import_csv(self):
        session = self.session_maker()
        import_playerstats_from_csv("tests/integration/ressources/player_stats.csv", session)

        season_1 = session.find_season(datetime.datetime(2023, 9, 15, 0, 0))
        season_1_bis = session.find_season(datetime.datetime(2023, 12, 1, 0, 0))
        self.assertEqual(season_1.id, season_1_bis.id)

        season_2 = session.find_season(datetime.datetime(2024, 10, 20, 0, 0))
        self.assertNotEqual(season_1.id, season_2.id)

        players = session.get_players([1, 2, 3], season_1.id)
        self.assertEqual(2, len(players))

        player = session.get_player(1, season_1.id)
        self.assertIsNotNone(player)
        self.assertEqual("Alice", player.name)
        self.assertEqual("FRI", player.club)
        self.assertEqual(False, player.foreigner)
        self.assertEqual("GK", player.role)

        player = session.get_player(2, season_1.id)
        self.assertIsNotNone(player)
        self.assertEqual("Bob", player.name)
        self.assertEqual("LAU", player.club)
        self.assertEqual(False, player.foreigner)
        self.assertEqual("FW", player.role)

        player = session.get_player(2, season_2.id)
        self.assertIsNotNone(player)
        self.assertEqual("Bob", player.name)
        self.assertEqual("LUG", player.club)
        self.assertEqual(False, player.foreigner)
        self.assertEqual("FW", player.role)

        player = session.get_player(3, season_2.id)
        self.assertIsNotNone(player)
        self.assertEqual("Eric", player.name)
        self.assertEqual("ZUG", player.club)
        self.assertEqual(True, player.foreigner)
        self.assertEqual("DF", player.role)

    def test_load_from_hm(self):
        user = os.getenv(HM_USER_ENV_NAME)
        password = os.getenv(HM_PASSWORD_ENV_NAME)

        def load_partial_data():  #
            parser = HMAjaxScrapper()
            parser.connect_to_hm(user, password)
            players_data = parser.get_players()[:2]  # limit test to 2 player
            for player in players_data:
                player.update(parser.get_player_stats(player['id']))
            parser.close_session()
            return players_data

        session = self.session_maker()
        import_playerstats_from_loader(load_partial_data, session, origin="AJAX")



if __name__ == '__main__':
    unittest.main()
