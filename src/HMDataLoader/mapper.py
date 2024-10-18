from datetime import date
from typing import Any

from HMDatabase import models


def _to_float(value: str) -> float:
    return float(value.replace(",", ".").replace('%', ''))


def _to_bool(value: str) -> bool:
    value = value.upper()
    return value == 'YES' or value == 'OUI' or value == "Y" or value == '1' or value == 'TRUE' or value == 'T'


FIELDS = {
    "id": int,
    "date": date.fromisoformat,
    "Price": _to_float,
    "Ownership": _to_float,
    "HM points": _to_float,
    "Appareances": int,
    "Goal": int,
    "Goal OT": int,
    "Assist #1": int,
    "Assist #2": int,
    "Assist OT": int,
    "Points": int,
    "GWG": int,
    "Penalties": int,
    "+/-":int,
    "Shots": int,
    "role": str,
    "name": str,
    "club": str,
    "foreigner": _to_bool
}


def _try_convert(data_dict: dict[str, str], field_name: str, type_cast):
    if field_name not in data_dict:
        return None
    field: str = data_dict[field_name]
    if field == "":
        return None
    try:
        return type_cast(field)
    except Exception as exception:
        print(f'Warning: invalid field cannot convert value "{field}" into type <{type_cast.__name__}>: {exception}')

        return None


def map_player_stats(player_stats_data: list[dict[str, str]]) -> (
        list[models.HockeyPlayer], list[models.HockeyPlayerStats]):
    player_stats_converted: list[dict[str, Any]] = []
    for player in player_stats_data:
        player_converted = {
            field_name: _try_convert(player, field_name, convertion)
            for field_name, convertion in FIELDS.items()
        }
        player_stats_converted.append(player_converted)

    players = [models.HockeyPlayer(id=player['id']
                                   , name=player['name']
                                   , club=player['club']
                                   , role=player['role']
                                   , foreigner=player['foreigner'])
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
