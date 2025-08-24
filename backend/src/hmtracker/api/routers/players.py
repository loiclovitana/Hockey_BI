from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from os import getenv
from hmtracker.constants import HM_DATABASE_URL_ENV_NAME
from hmtracker.database import repository as repo, models

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
async def get_players(session: SessionDep) -> list[dict]:
    """
    Get all players of the current season
    """
    players = session.get_players()
    return [models.to_json(p) for p in players]


@router.get("/{player_id}")
async def get_player(player_id: int, session: SessionDep):
    """
    Get the data of one player
    """
    players = session.get_players(player_ids=[player_id])
    if not players:
        raise HTTPException(status_code=404, detail="Player not found")
    return dict(players[0].__dict__)


@router.get("/stats")
async def get_players_stats(players_ids: list[int], session: SessionDep):
    players_stats = session.get_player_stats(players_ids)

    return [dict(ps.__dict__) for ps in players_stats]
