from typing import Annotated, Literal

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from hmtracker.api.admin_login import create_access_token
from pydantic import BaseModel
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


class AuthTokenResponse(BaseModel):
    type:Literal["bearer"] = "bearer"
    access_token:str
    

@api.post("/admin/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> AuthTokenResponse:
    access_token = create_access_token(
        username=form_data.username, password=form_data.password
    )
    return AuthTokenResponse(access_token=access_token)
