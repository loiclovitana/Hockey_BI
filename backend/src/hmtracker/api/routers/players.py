from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from os import getenv
from hmtracker.common.constants import HM_DATABASE_URL_ENV_NAME
from hmtracker.database import repository as repo
from hmtracker.api import models as api_models
from pydantic import BaseModel

router = APIRouter(prefix="/players", tags=["players"])

_HM_DATABASE_URL = getenv(HM_DATABASE_URL_ENV_NAME)
if _HM_DATABASE_URL is None:
    raise SystemError(f"{HM_DATABASE_URL_ENV_NAME} is not defined")
repo_session_maker = repo.create_repository_session_maker(_HM_DATABASE_URL)


def get_session():
    with repo_session_maker() as session:
        yield session


SessionDep = Annotated[repo.RepositorySession, Depends(get_session)]


@router.get("/")
async def get_players(session: SessionDep) -> list[api_models.HockeyPlayer]:
    """
    Get all players of the current season
    """
    players = session.get_players()
    return [api_models.HockeyPlayer.model_validate(p.__dict__) for p in players]


@router.get("/id/{player_id}")
async def get_player(player_id: int, session: SessionDep):
    """
    Get the data of one player
    """
    players = session.get_players(player_ids=[player_id])
    if not players:
        raise HTTPException(status_code=404, detail="Player not found")
    return api_models.HockeyPlayer.model_validate(players[0].__dict__)


@router.get("/stats/id/{player_id}")
async def get_player_stats(
    player_id: int, session: SessionDep
) -> list[api_models.HockeyPlayerStats]:
    players_stats = session.get_player_stats([player_id])

    if players_stats is None or len(players_stats) == 0:
        raise HTTPException(status_code=404, detail="No player found")
    return [
        api_models.HockeyPlayerStats.model_validate(stat.__dict__)
        for stat in players_stats
    ]


class LastPlayerStats(BaseModel):
    player_info: api_models.HockeyPlayer
    player_stats: api_models.HockeyPlayerStats | None


@router.get("/latest/")
async def get_latest_player_stats(session: SessionDep) -> list[LastPlayerStats]:
    players = [
        api_models.HockeyPlayer.model_validate(p.__dict__)
        for p in session.get_players()
    ]
    stats = session.get_current_player_stats([p.id for p in players])
    if stats is None:
        raise HTTPException(
            status_code=404, detail="No player stats could be found for current season"
        )
    current_players_stats = {
        stat.player_id: api_models.HockeyPlayerStats.model_validate(stat.__dict__)
        for stat in stats
    }

    last_player_stats = [
        LastPlayerStats(
            player_info=player, player_stats=current_players_stats.get(player.id)
        )
        for player in players
    ]
    return last_player_stats
