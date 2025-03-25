from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

from hmtracker.api.admin_login import create_access_token
from .routers import admin, players

app = FastAPI()

app.include_router(admin.router)
app.include_router(players.router)


@app.get("/ping")
async def ping_server():
    return True


@app.post("/admin/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = create_access_token(username=form_data.username, password=form_data.password)
    print(access_token)
    return {"access_token": access_token, "type": "bearer"}
