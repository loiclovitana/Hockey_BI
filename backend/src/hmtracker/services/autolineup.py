from hmtracker.parser.hmparser import HMAjaxScrapper


def autolineup(user_email: str, password: str):
    parser = HMAjaxScrapper()
    try:
        parser.connect_to_hm(user_email, password)

        teams = parser.get_teams()

        for team in teams:
            team_id = team["id"]
            parser.select_team(team_id)
            parser.auto_lineup()

    finally:
        parser.close_session()
