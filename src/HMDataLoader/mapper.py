from datetime import date
from typing import Any

from HMDatabase import models


def _try_convert(field: str, type_cast):
    try:
        return type_cast(field)
    except:
        print(f'Warning: invalid field cannot convert value "{field}" into type <{type_cast.__name__}>')
        return None


def map_player_stats(player_stats_data: list[dict[str, str]]) -> (
list[models.HockeyPlayer], list[models.HockeyPlayerStats]):
    def to_float(value: str) -> float:
        return float(value.replace(",", "."))

    player_stats_converted: list[dict[str, Any]] = []
    for player in player_stats_data:
        player_converted = dict()
        player_converted['id'] = _try_convert(player['id'], int)
        player_converted['date'] = _try_convert(player['date'], date.fromisoformat)
        player_converted['Price'] = _try_convert(player['Price'], to_float)
        player_converted['Ownership'] = _try_convert(player['Ownership'].replace('%', ''), to_float)
        player_converted['HM points'] = _try_convert(player['HM points'], to_float)
        player_converted['Appareances'] = _try_convert(player['Appareances'], int)
        player_converted['Goal'] = _try_convert(player['Goal'], int)
        player_converted['Goal OT'] = _try_convert(player['Goal OT'], int)
        player_converted['Assist #1'] = _try_convert(player['Assist #1'], int)
        player_converted['Assist #2'] = _try_convert(player['Assist #2'], int)
        player_converted['Assist OT'] = _try_convert(player['Assist OT'], int)
        player_converted['Points'] = _try_convert(player['Points'], int)
        player_converted['GWG'] = _try_convert(player['GWG'], int)
        player_converted['Penalties'] = _try_convert(player['Penalties'], int)
        player_converted['Shots'] = _try_convert(player['Shots'], int)

        player_stats_converted.append(player_converted)

    players = [models.HockeyPlayer(id=int(player['id'])
                                   , name=player['name']
                                   , club=player['club']
                                   , role=player['role'])
               for player in player_stats_converted]

    players_stats = [
        models.HockeyPlayerStats(
            player_id=player['id']
            , validity_date=player['date']
            , price=player['Price']
            , hm_points=player['HM points']
            , appearances=player['Appareances']
            , goal=player['Goal']
            , assists=None if player['Assist #1'] is None
            else player['Assist #1'] + player['Assist #2'] + player['Assist OT']
            , penalties=player['Penalties']
            , plus_minus=player['+/-']
        )
        for player in player_stats_converted
    ]
    return players, players_stats
