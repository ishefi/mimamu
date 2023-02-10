#!/usr/bin/env python
from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import routers
from session import get_mongo


def get_date_delta():
    today = datetime.utcnow().date()
    try:
        date = datetime.strptime(os.environ.get("GAME_DATE", ""), '%Y-%m-%d')
        return (date.date() - today).days
    except ValueError:
        return 0


app = FastAPI()
app.state.mongo = get_mongo()
app.state.date_delta = get_date_delta()
app.state.puzzle_version = os.environ.get("PUZZLE_VERSION", "")
app.state.secret_token = os.environ["SECRET_TOKEN"]

app.mount("/static", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router)
