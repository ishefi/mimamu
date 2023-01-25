#!/usr/bin/env python
import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import routers
from session import get_mongo

app = FastAPI()
app.state.mongo = get_mongo()
app.state.date = datetime.date.today() + datetime.timedelta(days=5)

app.mount("/static", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router)
