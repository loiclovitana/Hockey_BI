import argparse
import sys
from os import getenv
from random import randint
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from HMDataLoader.constants import HM_DATABASE_URL_ENV_NAME, HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME, HM_URL

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


def _random_number() -> str:
    return str(randint(10000000, 99999999))


def _parse_players_html_list(player_html_list: str):
    soup = BeautifulSoup(player_html_list, 'html.parser')
    # TODO
    return []


class HMAjaxParser:
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
        player_html_list = self._get_player_html_list(club=0) + self._get_player_html_list(club=1)
        return _parse_players_html_list(player_html_list)

    def get_player_stats(self, player_id):
        self._check_session_open()

    def close_session(self):
        if self.session is None:
            return
        self.session.close()
        self.session = None


def import_from_ajax(database_url, user, password):
    parser = HMAjaxParser()
    parser.connect_to_hm(user, password)

    players = parser.get_players()

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
