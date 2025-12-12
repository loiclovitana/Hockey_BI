from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from os import getenv
from hmtracker.common.constants import HM_DATABASE_URL_ENV_NAME
from hmtracker.database import repository as repo
from hmtracker.api import models as api_models
from hmtracker.loader.main import import_teamplayers_from_loader
from hmtracker.loader.teamplayers.source.website import team_players_ajax_loader
from hmtracker.services.check_user import connect_to_hm
from hmtracker.services.encryption import encrypt
from hmtracker.services.team_value import (
    TeamModification,
    TeamValue,
    compute_team_value_sql,
)
from pydantic import BaseModel, SecretStr

router = APIRouter(prefix="/myteam", tags=["myteam"])

_HM_DATABASE_URL = getenv(HM_DATABASE_URL_ENV_NAME)
if _HM_DATABASE_URL is None:
    raise SystemError(f"{HM_DATABASE_URL_ENV_NAME} is not defined")
repo_session_maker = repo.create_repository_session_maker(_HM_DATABASE_URL)


def get_session():
    with repo_session_maker() as session:
        yield session


SessionDep = Annotated[repo.RepositorySession, Depends(get_session)]


class AuthRequest(BaseModel):
    hm_user: str
    hm_password: SecretStr


class LoadRequest(AuthRequest):
    force_team_reload: bool = False


class DashBoardData(BaseModel):
    manager: api_models.Manager
    my_teams: list[list[api_models.Team]]


_CACHE_S = 600


@router.post("/load")
async def load(request: LoadRequest, session: SessionDep) -> DashBoardData:
    manager = session.get_manager_by_email(request.hm_user)
    if (
        manager is None
        or manager.last_import is None
        or (datetime.now() - manager.last_import).total_seconds() > _CACHE_S
        or request.force_team_reload
    ):
        loader = team_players_ajax_loader(
            request.hm_user, request.hm_password.get_secret_value()
        )
        import_teamplayers_from_loader(loader, request.hm_user, session)
    else:
        connect_to_hm(request.hm_user, password=request.hm_password.get_secret_value())

    manager = session.get_manager_by_email(request.hm_user)
    if manager is None:
        raise HTTPException(status_code=500, detail="Manager wasn't saved correctly")
    teams = [
        api_models.Team.model_validate(team.__dict__)
        for team in session.get_teams(manager=manager)
    ]

    # Group teams by team attribute and sort
    teams_by_group: dict[str, list[api_models.Team]] = {}
    for team in teams:
        group_key = team.team
        if group_key not in teams_by_group:
            teams_by_group[group_key] = []
        teams_by_group[group_key].append(team)

    # Sort groups by key and create sorted list of team lists
    sorted_team_groups = [teams_by_group[key] for key in sorted(teams_by_group.keys())]

    return DashBoardData(
        manager=api_models.Manager.model_validate(manager.__dict__),
        my_teams=sorted_team_groups,
    )


@router.post("/autolineup/register")
async def register_for_autolinup(
    request: AuthRequest, session: SessionDep
) -> api_models.Manager:
    manager = session.get_manager_by_email(request.hm_user)
    if manager is None:
        raise HTTPException(status_code=500, detail="Manager wasn't saved correctly")
    connect_to_hm(request.hm_user, password=request.hm_password.get_secret_value())

    manager.encrypted_password = encrypt(request.hm_password.get_secret_value())
    manager.autolineup = True
    response = api_models.Manager.model_validate(manager.__dict__)
    session.session.commit()
    return response


@router.post("/autolineup/unregister")
async def unregister_for_autolinup(
    request: AuthRequest, session: SessionDep
) -> api_models.Manager:
    manager = session.get_manager_by_email(request.hm_user)
    if manager is None:
        raise HTTPException(status_code=500, detail="Manager wasn't saved correctly")
    connect_to_hm(request.hm_user, password=request.hm_password.get_secret_value())
    manager.encrypted_password = None
    manager.autolineup = False
    response = api_models.Manager.model_validate(manager.__dict__)
    session.session.commit()
    return response


class TransfertModifications(BaseModel):
    modifications: List[TeamModification] = []


class TeamValueEvolution(BaseModel):
    evolution: list[TeamValue]


@router.post("/team_value_evolution")
async def team_value_evolution(
    request: AuthRequest,
    session: SessionDep,
    team_code: str,
    transfert_modification: TransfertModifications = TransfertModifications(),
) -> TeamValueEvolution:
    # Get the manager from the email
    manager = session.get_manager_by_email(request.hm_user)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Verify credentials
    connect_to_hm(request.hm_user, password=request.hm_password.get_secret_value())

    # Get current season
    current_season = session.get_current_season()
    if current_season is None:
        raise HTTPException(status_code=404, detail="No current season found")

    evolution = compute_team_value_sql(
        repository=session,
        manager_id=manager.id,
        season_id=current_season.id,
        team_code=team_code,
        modifications=transfert_modification.modifications
        if transfert_modification.modifications
        else None,
    )

    return TeamValueEvolution(evolution=evolution)
