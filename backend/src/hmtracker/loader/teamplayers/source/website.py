from collections.abc import Callable

from hmtracker.parser.hmparser import HMAjaxScrapper


def team_players_ajax_loader(user: str, password: str) -> Callable:
    """
    Create a loader method that can be call to return the players of a given HM user.
    :param user: user login
    :param password: user password
    :return: the method to load the hockey players in the user team
    """
    if user is None or password is None:
        raise ConnectionRefusedError("User password to connect to HM are not provided")

    def load_data() -> dict[str, list[int]]:
        parser = HMAjaxScrapper()
        teams_players = dict()
        try:
            parser.connect_to_hm(user, password)

            teams = parser.get_teams()

            for team in teams:
                team_id = team["id"]
                parser.select_team(team_id)
                teams_players[team_id] = [
                    player["id"] for player in parser.get_current_team()
                ]

        finally:
            parser.close_session()
        return teams_players

    return load_data
