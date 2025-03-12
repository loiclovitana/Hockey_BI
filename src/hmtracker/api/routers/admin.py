from fastapi import APIRouter
from hmtracker import admin


router = APIRouter(
    prefix="/admin"
)


@router.get("/load/start")
def start_loading():
    admin.start_loading()