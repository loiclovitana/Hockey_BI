import logging
from datetime import date
from typing import Any

from hmtracker.database import models


def _to_float(value: str) -> float:
    return float(value.replace(",", ".").replace('%', ''))


def _to_bool(value: str) -> bool | None:
    value = value.upper()
    if value == 'YES' or value == 'OUI' \
            or value == "Y" or value == '1' \
            or value == 'TRUE' or value == 'T':
        return True
    if value == 'NO' or value == 'NON' \
            or value == "N" or value == '0' \
            or value == 'FALSE' or value == 'F':
        return False
    raise EncodingWarning(f"Boolean value for {value} cannot be converted")


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
    "+/-": int,
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
        logging.warning(f'Invalid field cannot convert value "{field}" into type <{type_cast.__name__}>: {exception}')
        return None


def _convert_data(player_stats_data: list[dict[str, str]]) -> list[dict[str, Any]]:
    player_stats_converted: list[dict[str, Any]] = []
    for player in player_stats_data:
        player_converted = {
            field_name: _try_convert(player, field_name, convertion)
            for field_name, convertion in FIELDS.items()
        }
        player_stats_converted.append(player_converted)
    return player_stats_converted


def map_player_stats(player_stats_data: list[dict[str, str]]) -> (
        list[models.HockeyPlayer], list[models.HockeyPlayerStats]):
    player_stats_converted: list[dict[str, Any]] = _convert_data(player_stats_data)

    players = [models.HockeyPlayer(id=player['id']
                                   , name=player['name']

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
            , ownership=player['Ownership']
            , goal=player['Goal']
            , club=player['club']
            , assists=None if player['Assist #1'] is None
            else player['Assist #1'] + player['Assist #2'] + player['Assist OT']
            , penalties=player['Penalties']
            , plus_minus=player['+/-']
        )
        for player in player_stats_converted
    ]
    return players, players_stats
