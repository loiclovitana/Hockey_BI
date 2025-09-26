from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from hmtracker.services import admin
from hmtracker.api.admin_login import admin_login_scheme, decode_token
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(admin_login_scheme)]
)


@router.post("/load/start")
def start_loading() -> None:
    admin.start_loading()

@router.post("/autoteam/start")
def start_team_alignement() -> None:
    admin.start_team_alignement()

class AdminUser(BaseModel):
    username:str


@router.get("/user")
def get_admin_user(token: Annotated[str, Depends(admin_login_scheme)]) ->AdminUser:
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
