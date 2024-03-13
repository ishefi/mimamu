#!/usr/bin/env python
import hashlib
from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import routers
from session import get_mongo


def get_date_delta() -> int:
    today = datetime.utcnow().date()
    try:
        date = datetime.strptime(os.environ.get("GAME_DATE", ""), "%Y-%m-%d")
        return (date.date() - today).days
    except ValueError:
        return 0


STATIC_FOLDER = "static"
js_hasher = hashlib.sha3_256()
with open(STATIC_FOLDER + "/mimamu.js", "rb") as f:
    js_hasher.update(f.read())
JS_VERSION = js_hasher.hexdigest()[:8]

css_hasher = hashlib.sha3_256()
with open(STATIC_FOLDER + "/styles.css", "rb") as f:
    css_hasher.update(f.read())
CSS_VERSION = css_hasher.hexdigest()[:8]

app = FastAPI()
app.state.mongo = get_mongo()
app.state.date_delta = get_date_delta()
app.state.puzzle_version = os.environ.get("PUZZLE_VERSION", "")
app.state.secret_token = os.environ["SECRET_TOKEN"]
app.state.js_version = JS_VERSION
app.state.css_version = CSS_VERSION

app.mount(f"/{STATIC_FOLDER}", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router)
