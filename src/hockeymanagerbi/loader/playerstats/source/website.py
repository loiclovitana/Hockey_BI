from collections.abc import Callable

from hockeymanagerbi.loader.constants import HM_URL
from hockeymanagerbi.parser.hmparser import HMAjaxScrapper



def playerstats_ajax_loader(user: str, password: str) -> Callable[[], list[dict[str, str]]]:
    """
    :param user: login for Hockey manager website
    :param password:
    :return: A callable to get the data
    """
    if user is None or password is None:
        raise ConnectionRefusedError("User password to connect to HM are not provided")

    def load_data():
        parser = HMAjaxScrapper()
        try:
            parser.connect_to_hm(user, password)

            players_data = parser.get_all_players()
            for player in players_data:
                player.update(parser.get_player_stats(player['id']))
        finally:
            parser.close_session()
        return players_data

    return load_data


def team_players_ajax_loader(user: str, password: str):
    if user is None or password is None:
        raise ConnectionRefusedError("User password to connect to HM are not provided")

    def load_data():
        parser = HMAjaxScrapper()
        try:
            parser.connect_to_hm(user, password)

            teams = parser.get_teams()

            players_data = []
            for team in teams:
                team_id = team['id']
                parser.select_team(team_id)
                players_data += [(team_id, player['id']) for player in parser.get_current_team()]

        finally:
            parser.close_session()
        return players_data

    return load_data
