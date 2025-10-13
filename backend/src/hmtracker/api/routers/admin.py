from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request, UploadFile, File
from fastapi import HTTPException, status
from hmtracker.services import admin
from hmtracker.api.admin_login import admin_login_scheme, decode_token
from hmtracker.database import repository as repo
from hmtracker.api import models as api_models
from hmtracker.common.constants import HM_DATABASE_URL_ENV_NAME
from hmtracker.loader.matches.mapper import parse_match_csv
from hmtracker.loader.matches.importer import import_matches
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


class MatchImportResponse(BaseModel):
    new_matches: int
    updated_matches: int
    message: str


@router.post("/matches/upload", response_model=MatchImportResponse)
async def upload_matches_csv(
    request: Request,
    session: SessionDep,
    file: UploadFile = File(...),
) -> MatchImportResponse:
    """
    Upload a CSV file containing match data.
    The file should be in the format with columns for date, time, home team, away team, and match ID.
    Existing matches (by ID) will be updated, new matches will be inserted.
    Maximum file size: 5MB.
    """

    # Check file size before reading (5MB limit)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 5MB limit",
        )

    # Validate file type
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV file"
        )

    try:
        # Read file content
        content = await file.read()

        # Decode bytes to string
        csv_content = content.decode("utf-8-sig")

        # Parse CSV to Match objects
        matches = parse_match_csv(csv_content)

        if not matches:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid matches found in CSV file",
            )

        # Import matches to database
        new_count, updated_count = import_matches(session, matches)

        # Commit the transaction
        session.session.commit()

        return MatchImportResponse(
            new_matches=new_count,
            updated_matches=updated_count,
            message=f"Successfully imported {new_count} new matches and updated {updated_count} existing matches",
        )

    except Exception as e:
        session.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import matches: {str(e)}",
        )
