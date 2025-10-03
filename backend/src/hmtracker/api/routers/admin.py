from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException, status
from hmtracker.services import admin
from hmtracker.api.admin_login import admin_login_scheme, decode_token
from hmtracker.database import repository as repo
from hmtracker.api import models as api_models
from hmtracker.common.constants import HM_DATABASE_URL_ENV_NAME
from pydantic import BaseModel
from os import getenv

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(admin_login_scheme)]
)

_HM_DATABASE_URL = getenv(HM_DATABASE_URL_ENV_NAME)
if _HM_DATABASE_URL is None:
    raise SystemError(f"{HM_DATABASE_URL_ENV_NAME} is not defined")
repo_session_maker = repo.create_repository_session_maker(_HM_DATABASE_URL)


def get_session():
    with repo_session_maker() as session:
        yield session


SessionDep = Annotated[repo.RepositorySession, Depends(get_session)]


@router.post("/load/start")
def start_loading() -> None:
    admin.start_loading()


@router.post("/autoteam/start")
def start_team_alignement() -> None:
    admin.start_team_alignement()


class AdminUser(BaseModel):
    username: str


@router.get("/user")
def get_admin_user(token: Annotated[str, Depends(admin_login_scheme)]) -> AdminUser:
    username = decode_token(token)
    return AdminUser(username=username)


@router.get("/operation")
def get_operation() -> str:
    operation_name = admin.get_current_operation()
    if operation_name:
        return operation_name
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, detail="No operation are currently running"
    )


@router.get("/tasks")
async def get_tasks(
    session: SessionDep,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[api_models.Task]:
    """
    Get tasks with pagination, ordered by most recent first
    """
    tasks = session.get_tasks(limit=limit, offset=offset)
    return [api_models.Task.model_validate(task.__dict__) for task in tasks]
