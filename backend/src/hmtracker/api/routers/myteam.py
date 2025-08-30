from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from os import getenv
from hmtracker.constants import HM_DATABASE_URL_ENV_NAME
from hmtracker.database import repository as repo, models
from hmtracker.api import models as api_models
from hmtracker.loader.main import import_teamplayers_from_loader
from hmtracker.loader.teamplayers.source.website import team_players_ajax_loader
from pydantic import BaseModel

router = APIRouter(prefix="/myteam", tags=["myteam"])

_HM_DATABASE_URL = getenv(HM_DATABASE_URL_ENV_NAME)
if _HM_DATABASE_URL is None:
    raise SystemError(f"{HM_DATABASE_URL_ENV_NAME} is not defined")
repo_session_maker = repo.create_repository_session_maker(_HM_DATABASE_URL)


def get_session():
    with repo_session_maker() as session:
        yield session


SessionDep = Annotated[repo.RepositorySession, Depends(get_session)]


class DashBoardData(BaseModel):
    my_teams:list[api_models.Team]
    

@router.post("/load")
async def load(hm_user:str,hm_password:str,session: SessionDep) -> DashBoardData:
    loader = team_players_ajax_loader(hm_user, hm_password)
    import_teamplayers_from_loader(
        loader, hm_user, session
    )
    manager = session.get_manager_by_email(hm_user)
    if manager is None:
        raise HTTPException(status_code=500,detail="Manager wasn't saved correctly")
    
    return  DashBoardData(
        my_teams=[ api_models.Team.model_validate(team.__dict__) for team in session.get_teams(manager=manager)]
    )
