#!/usr/bin/env python
import hashlib
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from common import config
from routers import routers


def get_date_delta() -> int:
    today = datetime.utcnow().date()
    try:
        date = datetime.strptime(config.GAME_DATE, "%Y-%m-%d")
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
app.state.date_delta = get_date_delta()
app.state.puzzle_version = config.PUZZEL_VERSION
app.state.js_version = JS_VERSION
app.state.css_version = CSS_VERSION

app.mount(f"/{STATIC_FOLDER}", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router)
