from random import randint
from collections.abc import Callable
from urllib.parse import quote

import bs4.element
import requests
from bs4 import BeautifulSoup

from hockeymanagerbi.loader.constants import HM_URL

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


def playerstats_ajax_loader(user, password) -> Callable[[], list[dict[str, str]]]:
    """
    :param user: login for Hockey manager website
    :param password:
    :return: A callable to get the data
    """

    def load_data():
        parser = HMAjaxScrapper()
        parser.connect_to_hm(user, password)

        players_data = parser.get_players()
        for player in players_data:
            player.update(parser.get_player_stats(player['id']))

        parser.close_session()
        return players_data

    return load_data


class HMAjaxScrapper:
    """
        Scrapper for HockeyManager website
    """
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

        return _scrap_player_details(response.text)

    def close_session(self):
        if self.session is None:
            return
        self.session.close()
        self.session = None


def _random_number() -> str:
    return str(randint(10000000, 99999999))


def _scrap_player_row(player_row_html: bs4.element.Tag) -> dict[str, str]:
    return {
        "id": player_row_html.attrs['attr']
        , "name": player_row_html.select('.name')[0].text
        , "club": player_row_html.img.attrs['src'].split('/')[-2]
        , "role": player_row_html.div.text
        , "foreigner": str(len(player_row_html.select(".ch")) != 0)
    }


def _scrap_player_details(player_details_html) -> dict[str, str]:
    soup = BeautifulSoup(player_details_html, 'html.parser')
    return {hist.attrs['label']: hist.attrs['value'] for hist in soup.select(".histogram.horiz")}


def _scrap_players_html_list(player_html_list: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(player_html_list, 'html.parser')
    players_rows = soup.select(".row")
    return [_scrap_player_row(player_row_html) for player_row_html in players_rows]
