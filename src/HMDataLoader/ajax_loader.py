import argparse
import sys
from datetime import datetime
from os import getenv
from random import randint
from urllib.parse import quote

import bs4.element
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from HMDataLoader.constants import HM_DATABASE_URL_ENV_NAME, HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME, HM_URL
from HMDatabase import models
from HMDatabase.repository import RepositorySession, create_repository_session_maker

AJAX_URL = HM_URL + "ajaxrequest/"

REQUEST_HEADER = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Content-Length": "90",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": HM_URL.replace("https://", "")[:-1],
    "Origin": HM_URL,
    "Referer": HM_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest"
}


def __connect_session(db_access: str | Session | RepositorySession) -> RepositorySession:
    if isinstance(db_access, str):
        return create_repository_session_maker(db_access)()
    if isinstance(db_access, Session):
        return RepositorySession(db_access)
    if isinstance(db_access, RepositorySession):
        return db_access
    raise ValueError("Database session must be provided")


def _random_number() -> str:
    return str(randint(10000000, 99999999))


def _scrap_player_row(player_row_html: bs4.element.Tag):
    player = models.HockeyPlayer(
        id=int(player_row_html.attrs['attr'])
        , name=player_row_html.select('.name')[0].text
        , club=player_row_html.img.attrs['src'].split('/')[-2]
        , role=player_row_html.div.text
    )
    return player


def _scrap_player_details(player_details_html):
    def try_convert(field: str, type_cast):
        try:
            return type_cast(field)
        except:
            print(f'Warning: invalid field cannot convert value "{field}" into type <{type_cast.__name__}>')
            return None

    soup = BeautifulSoup(player_details_html, 'html.parser')

    stats = {hist.attrs['label']: hist.attrs['value'] for hist in soup.select(".histogram.horiz")}
    # TODO clean up duplicates
    stats['Price'] = try_convert(stats['Price'], float)
    stats['Ownership'] = try_convert(stats['Ownership'].replace('%', ''), float)
    stats['HM points'] = try_convert(stats['HM points'], float)
    stats['Appareances'] = try_convert(stats['Appareances'], int)
    stats['Goal'] = try_convert(stats['Goal'], int)
    stats['Goal OT'] = try_convert(stats['Goal OT'], int)
    stats['Assist #1'] = try_convert(stats['Assist #1'], int)
    stats['Assist #2'] = try_convert(stats['Assist #2'], int)
    stats['Assist OT'] = try_convert(stats['Assist OT'], int)
    stats['Points'] = try_convert(stats['Points'], int)
    stats['GWG'] = try_convert(stats['GWG'], int)
    stats['Penalties'] = try_convert(stats['Penalties'], int)

    return models.HockeyPlayerStats(
        price=stats['Price']
        , hm_points=stats['HM points']
        , appearances=stats['Appareances']
        , goal=stats['Goal']
        , assists=None if stats['Assist #1'] is None
        else int(stats['Assist #1']) + int(stats['Assist #2']) + int(stats['Assist OT'])
        , penalties=stats['Penalties']
        , plus_minus=stats['+/-']
    )


def _scrap_players_html_list(player_html_list: str):
    soup = BeautifulSoup(player_html_list, 'html.parser')
    players_rows = soup.select(".row")
    return [_scrap_player_row(player_row_html) for player_row_html in players_rows]


class HMAjaxScrapper:
    session = None

    def _check_session_open(self):
        if self.session is None:
            raise ConnectionError("Parser isn't connected to Hockey Manager")

    def connect_to_hm(self, user, password):
        self.session = requests.session()
        self.session.headers.update(REQUEST_HEADER)

        query_data = (f"fh_u={quote(user)}&"
                      f"fh_p={quote(password)}&"
                      f"randomNumber={_random_number()}")

        response = self.session.post(AJAX_URL + "try-login", query_data)
        connection_success = response.status_code == 200 and response.text == '1'
        if not connection_success:
            raise ConnectionError(f"Couldn't connect to Hockey Manager: <{response.status_code}>")

    def _get_player_html_list(self, club: int = 0):
        query_data = (f"randomNumber={_random_number()}&"
                      f"club={club}&"
                      f"role=0&player=&min=1&max=50&country=0&blG=0&blP=0&orderBy=&orderByDirection=")
        response = self.session.post(AJAX_URL + "transfers-classic-get-list-preview", query_data)
        connection_success = response.status_code == 200 and len(response.text) != 0
        if not connection_success:
            raise ConnectionError(f"Couldn't query the players list from: <{response.status_code}>")
        return response.text

    def get_players(self):
        self._check_session_open()
        player_html_list = self._get_player_html_list(club=0) + self._get_player_html_list(club=-1)
        return _scrap_players_html_list(player_html_list)

    def get_player_stats(self, player_id):
        self._check_session_open()
        query_data = f"id={player_id}"
        print(f"Query {player_id}")
        response = self.session.post(AJAX_URL + "get-player-detail", query_data)
        connection_success = response.status_code == 200 and len(response.text) != 0
        if not connection_success:
            raise ConnectionError(f"Couldn't query the players list from: <{response.status_code}>")
        player_stats: models.HockeyPlayerStats = _scrap_player_details(response.text)
        player_stats.player_id = player_id
        return player_stats

    def close_session(self):
        if self.session is None:
            return
        self.session.close()
        self.session = None


def import_from_ajax(db_access: Session | str, user, password):
    parser = HMAjaxScrapper()
    parser.connect_to_hm(user, password)

    players = parser.get_players()
    players_id = [player.id for player in players]

    importation = models.StatImport(validity_date=datetime.now(),
                                    origin='Hockey Manager',
                                    comment="")
    players_stats = [
        parser.get_player_stats(player.id)
        for player in players
    ]

    for stats in players_stats:
        stats.importation = importation
        stats.validity_date = datetime.now()

    database_session: RepositorySession = __connect_session(db_access)
    current_season: models.Season = database_session.get_current_season()

    existing_players: set[str] = {player.id
                                  for player in database_session.get_players(players_id, current_season.id)}
    new_players = []
    for player in players:
        if player.id not in existing_players:
            existing_players.add(player.id)
            player.season_id = current_season.id
            new_players.append(player)

    database_session.session.add_all(new_players)
    database_session.session.add(importation)

    database_session.end_session()
    parser.close_session()


if __name__ == '__main__':

    argument_parser = argparse.ArgumentParser(
        description="Load data from hockey manager using ajax queries into a database"
    )

    argument_parser.add_argument("-d", "--database-url", default=getenv(HM_DATABASE_URL_ENV_NAME)
                                 , help=f"""Connection string to connect to the database were to save the data.
                                 If not set, use environment variable {HM_DATABASE_URL_ENV_NAME}""")
    argument_parser.add_argument("-u", "--hm-user", default=getenv(HM_USER_ENV_NAME)
                                 , help=f"""User login to connect to Hockey Manager.
                                     If not set, use environment variable {HM_USER_ENV_NAME}""")
    argument_parser.add_argument("-p", "--hm-password", default=getenv(HM_PASSWORD_ENV_NAME)
                                 , help=f"""Password for login to HockeyManager.
                                     If not set, use environment variable {HM_PASSWORD_ENV_NAME}""")


    def check_exists(argument, name):
        if argument is None:
            print(f"Error: Missing argument {name}.")
            argument_parser.print_help()
            sys.exit(1)


    arguments = argument_parser.parse_args()
    check_exists(arguments.database_url, 'database-url')
    check_exists(arguments.hm_user, 'hm-user')
    check_exists(arguments.hm_password, 'hm-password')

    import_from_ajax(arguments.database_url, arguments.hm_user, arguments.hm_password)
