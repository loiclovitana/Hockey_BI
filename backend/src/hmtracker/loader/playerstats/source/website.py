from collections.abc import Callable

from hmtracker.parser.hmparser import HMAjaxScrapper


def playerstats_ajax_loader(
    user: str, password: str
) -> Callable[[], list[dict[str, str]]]:
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
                player.update(parser.get_player_stats(player["id"]))
        finally:
            parser.close_session()
        return players_data

    return load_data
