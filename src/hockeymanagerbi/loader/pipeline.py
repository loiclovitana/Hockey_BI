import os
from collections.abc import Callable

from hockeymanagerbi.loader.constants import HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME

from hockeymanagerbi.loader.playerstats.source.ajax import playerstats_ajax_loader
from hockeymanagerbi.loader.playerstats.mapper import map_player_stats
from hockeymanagerbi.loader.playerstats.importer import import_hockey_stats_data

LOAD_PLAYER_STATS_FROM_HOCKEY_MANAGER: tuple[Callable, Callable, Callable] = (
    playerstats_ajax_loader(os.getenv(HM_USER_ENV_NAME), os.getenv(HM_PASSWORD_ENV_NAME))
    , map_player_stats
    , import_hockey_stats_data
)

