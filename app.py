#!/usr/bin/env python
from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import routers
from session import get_mongo


def get_date():
    try:
        date = datetime.strptime(os.environ.get("GAME_DATE", ""), '%Y-%m-%d')
        return date.date()
    except ValueError:
        return datetime.utcnow().date()


app = FastAPI()
app.state.mongo = get_mongo()
app.state.date = get_date()

app.mount("/static", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router)
