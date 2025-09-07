from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from hmtracker.api.admin_login import create_access_token
from .routers import admin, players, myteam

api = FastAPI()
app = CORSMiddleware(
    app=api,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers="*",
)

api.include_router(admin.router)
api.include_router(players.router)
api.include_router(myteam.router)


@api.get("/ping")
async def ping_server():
    return True


@api.post("/admin/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = create_access_token(
        username=form_data.username, password=form_data.password
    )
    return {"access_token": access_token, "type": "bearer"}
