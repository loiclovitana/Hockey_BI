from fastapi import FastAPI
from os import getenv
from hmtracker.database import repository as repo

from .routers import admin

app = FastAPI()
repo_session_maker = repo.create_repository_session_maker(getenv("HM_DATABASE_URL"))

app.include_router(admin.router)


@app.get("/all-players")
async def get_players():
    session: repo.RepositorySession = repo_session_maker()
    players = session.get_players()
    p = dict(players._mapping)
    session.end_session()
    return p


@app.get("/ping")
async def ping_server():
    return True
