from typing import Annotated, Literal

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from hmtracker.api.admin_login import create_access_token
from hmtracker.common.exceptions import HMAuthenticationError, HMUnavailableError
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


@api.exception_handler(HMAuthenticationError)
async def hm_authentication_error(request: Request, exc: HMAuthenticationError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@api.exception_handler(HMUnavailableError)
async def hm_unavailable_error(request: Request, exc: HMUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@api.get("/ping")
async def ping_server():
    return True


class AuthTokenResponse(BaseModel):
    type: Literal["bearer"] = "bearer"
    access_token: str


@api.post("/admin/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AuthTokenResponse:
    access_token = create_access_token(
        username=form_data.username, password=form_data.password
    )
    return AuthTokenResponse(access_token=access_token)
