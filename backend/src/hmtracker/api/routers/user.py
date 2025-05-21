from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from os import getenv
from hmtracker.database import repository as repo, models
from pydantic import BaseModel

router = APIRouter(
    prefix="/manager",
    tags=["managers"]
)

repo_session_maker = repo.create_repository_session_maker(getenv("HM_DATABASE_URL"))


def get_session():
    with repo_session_maker() as session:
        yield session

class HMManager(BaseModel):
    email: str
    password: str

SessionDep = Annotated[repo.RepositorySession, Depends(get_session)]


@router.put("/")
async def update_manager(manager:HMManager,session: SessionDep) -> list[dict]:
    """
    Add a manager to the database with all its players or update the players of the given manager
    """
    
    return True