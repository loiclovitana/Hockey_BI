from urllib.parse import quote
from random import randint
import logging
import bs4.element
import requests
from bs4 import BeautifulSoup
from requests import Session

from hmtracker.constants import HM_URL

AJAX_URL = HM_URL + "ajaxrequest/"

AJAX_REQUEST_HEADER = {
    "Accept": "*/*",
    "Accept-Encoding": "identity",
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
    "X-Requested-With": "XMLHttpRequest",
}

PAGE_REQUEST_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


class HMAjaxScrapper:
    """
    Scrapper for HockeyManager website
    """

    def __init__(self) -> None:
        self.session: Session | None = None
        self.dashboard: BeautifulSoup | None = None  # Cached for navigation

    def connect_to_hm(self, user, password):
        self.session = requests.session()
        query_data = (
            f"fh_u={quote(user)}&fh_p={quote(password)}&randomNumber={_random_number()}"
        )

        response = self.session.post(
            AJAX_URL + "try-login", query_data, headers=AJAX_REQUEST_HEADER
        )
        connection_success = response.status_code == 200 and "1" == response.text
        if not connection_success:
            raise ConnectionError(
                f"Couldn't connect to Hockey Manager: <{response.status_code}>\n{response.text}"
            )
        self._load_main_dashboard()

    def get_all_players(self):
        """
        :return: a list containing information of all players in HM
        """
        player_html_list = self._get_player_html_list(club=0)
        try:
            player_html_list += self._get_player_html_list(club=-1)
        except ConnectionError:
            logging.warning(
                "Couldn't get player team, maybe the admin still doesn't have a team. "
            )
        return _scrap_players_html_list(player_html_list)

    def get_player_stats(self, player_id):
        """
        :param player_id:
        :return: dictionary of statistics for a given player
        """
        session = self._get_open_session()
        query_data = f"id={player_id}"
        logging.debug(f"==> POST get-player-detail {player_id} {{{query_data}}}")
        response = session.post(
            AJAX_URL + "get-player-detail", query_data, headers=AJAX_REQUEST_HEADER
        )
        logging.debug(f"<== {response.status_code} {{{response.text}}}")
        connection_success = response.status_code == 200 and len(response.text) != 0
        if not connection_success:
            raise ConnectionError(
                f"Couldn't query the players list from: <{response.status_code}>"
            )

        return _scrap_player_details(response.text)

    def get_teams(self):
        """
        :return: data about the existing teams of the player
        """
        teams_soups = self.dashboard.select(".is-a-team.selectTeam")

        def _get_points_rank(team_soup):
            """Get the ranking position and points of a team
            If none exist return only the points to 0 since the season did not start
            """
            points_rank = team_soup.find(attrs={"class": "team-rank"})
            if points_rank is None:
                return {"points": 0}
            try:
                points, rank = points_rank.text.split("/")
                return {
                    "points": int(points.replace("'", "")),
                    "rank": int(rank.replace("'", "").replace("e", "")),
                }
            except ValueError:
                return {"points": 0}

        return [
            {
                "id": team_soup["attr"],
                "name": team_soup.find(attrs={"class": "team-name"}).text,
                **_get_points_rank(team_soup),
            }
            for team_soup in teams_soups
        ]

    def select_team(self, team_id):
        session = self._get_open_session()
        query_data = f"randomNumber={_random_number()}&myteam={team_id}"
        response = session.post(
            AJAX_URL + "use-team", query_data, headers=AJAX_REQUEST_HEADER
        )
        if response.status_code != 200:
            raise ConnectionError(
                f"Could not select the team: Error {response.status_code} - {response.text}"
            )
        if not response.text:
            raise ConnectionError(f"Could not select the team {team_id}")

    def get_current_team(self):
        """
        :return: a list of all player in the selected team
        """
        player_html_list = self._get_player_html_list(club=0)
        return _scrap_players_html_list(player_html_list)

    def close_session(self):
        if self.session is None:
            return
        self.session.close()
        self.session = None

    def _get_open_session(self) -> Session:
        if self.session is None:
            raise ConnectionError("Parser isn't connected to Hockey Manager")
        return self.session

    def _load_main_dashboard(self):
        """
        Load the main page of Hockey Manager.
        If the gamemode is arcade, switch to original
        :return: None
        """
        session = self._get_open_session()
        MAX_ATTEMPTS = 5
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            response = session.get(
                HM_URL + "/fr/dashboard", headers=PAGE_REQUEST_HEADER
            )
            dashboard_soup = BeautifulSoup(response.text, features="html.parser")
            if response.status_code != 200:
                continue
            if _is_arcade(dashboard_soup):
                query_data = f"randomNumber={_random_number()}"
                session.post(
                    AJAX_URL + "switch-classic-arcade",
                    query_data,
                    headers=AJAX_REQUEST_HEADER,
                )  # switch mode
            else:
                self.dashboard = dashboard_soup
                break
            attempts += 1
        if attempts == MAX_ATTEMPTS:
            raise Exception("Couldn't load the main page for HM")

    def _get_player_html_list(self, club: int = 0):
        session = self._get_open_session()
        query_data = (
            f"randomNumber={_random_number()}&"
            f"club={club}&"
            f"role=0&player=&min=1&max=50&country=0&blG=0&blP=0&orderBy=&orderByDirection="
        )
        response = session.post(
            AJAX_URL + "transfers-classic-get-list-preview",
            query_data,
            headers=AJAX_REQUEST_HEADER,
        )
        connection_success = response.status_code == 200 and len(response.text) != 0
        if not connection_success:
            raise ConnectionError(
                f"Couldn't query the players list from: <{response.status_code}>"
            )
        return response.text


def _random_number() -> str:
    return str(randint(10000000, 99999999))


def _scrap_player_row(player_row_html: bs4.element.Tag) -> dict[str, str]:
    return {
        "id": player_row_html.attrs["attr"],
        "name": player_row_html.select(".name")[0].text,
        "club": player_row_html.img.attrs.get("src", "/").split("/")[-2]
        if player_row_html.img
        else "",
        "role": player_row_html.div.text if player_row_html.div else "",
        "foreigner": str(len(player_row_html.select(".ch")) != 0),
    }


def _scrap_player_details(player_details_html) -> dict[str, str]:
    soup = BeautifulSoup(player_details_html, "html.parser")
    return {
        hist.attrs["label"]: hist.attrs["value"]
        for hist in soup.select(".histogram.horiz")
    }


def _scrap_players_html_list(player_html_list: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(player_html_list, "html.parser")
    players_rows = soup.select(".row")
    return [_scrap_player_row(player_row_html) for player_row_html in players_rows]


def _is_arcade(soup):
    logos = soup.select(".logo-hm")
    return logos and "arcade" in str(logos[0])
