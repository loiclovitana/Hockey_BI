from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from hmtracker import admin
from hmtracker.api.admin_login import admin_login_scheme

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(admin_login_scheme)]
)


@router.post("/load/start")
def start_loading() -> None:
    admin.start_loading()


@router.get("/operation")
def get_operation() -> str:
    operation_name = admin.get_current_operation()
    if operation_name:
        return operation_name
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No operation are currently running")
