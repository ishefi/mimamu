#!/usr/bin/env python
import datetime
from typing import Annotated
from typing import Any

import pymongo
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import schemas
from auth import verify_token
from common import config
from logic import ParseRiddleLogic
from logic import RiddleLogic
from session import get_mongo

templates = Jinja2Templates(directory="templates")
page_router = APIRouter()
game_router = APIRouter(prefix="/game")
admin_router = APIRouter(prefix="/admin", dependencies=[Depends(verify_token)])


def render(name: str, request: Request, **kwargs: Any) -> HTMLResponse:
    kwargs["js_version"] = request.app.state.js_version
    kwargs["css_version"] = request.app.state.css_version
    kwargs["lang"] = request.cookies.get("lang", "en")
    kwargs["content"] = config.html_content
    kwargs["request"] = request
    return templates.TemplateResponse(
        name,
        context=kwargs,
    )


@page_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request) -> HTMLResponse:
    return render(name="index.html", request=request)


@page_router.get("/history", response_class=HTMLResponse, include_in_schema=False)
async def history(request: Request) -> HTMLResponse:
    return render(name="history.html", request=request)


@page_router.get("/lang/{lang}", response_class=RedirectResponse)
async def language_change(request: Request, lang: str) -> RedirectResponse:
    response = RedirectResponse("/")
    response.set_cookie("lang", lang)
    return response


def get_logic(
    request: Request,
    mongo: dict[str, pymongo.collection.Collection[schemas.GameDataDict]] = Depends(
        get_mongo
    ),
    lang: str | None = Query(None),
) -> RiddleLogic:
    days_delta = datetime.timedelta(days=request.app.state.date_delta)
    date = datetime.datetime.utcnow().date() + days_delta
    return RiddleLogic(
        mongo_riddles=mongo,
        date=date,
        lang=lang or request.cookies.get("lang", "en"),
    )


@game_router.get("/data")
async def get_game(logic: RiddleLogic = Depends(get_logic)) -> schemas.GameData:
    return logic.get_redacted_riddle()


@game_router.get("/guess")
async def guess(
    guess_word: str, logic: RiddleLogic = Depends(get_logic)
) -> schemas.GuessAnswer:
    guess_answer = schemas.GuessAnswer()
    for word in guess_word.split():
        guess_answer.update(logic.guess(word.strip()))
    return guess_answer


@game_router.get("/version")
async def get_puzzle_version(request: Request) -> dict[str, str]:
    return {"version": request.app.state.puzzle_version}


@game_router.get("/history")
async def get_history(
    page: Annotated[int, Query(ge=0)], logic: RiddleLogic = Depends(get_logic)
) -> list[schemas.GameData]:
    return logic.get_history(page)


@game_router.get("/first-date")
async def get_first_date(
    logic: RiddleLogic = Depends(get_logic),
) -> dict[str, datetime.datetime]:
    return {"first_date": logic.get_first_riddle_date()}


@admin_router.delete("/cache", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cache(logic: RiddleLogic = Depends(get_logic)) -> None:
    logic.clear_cache()


@admin_router.get("/set-riddle", include_in_schema=False)
async def set_riddle(request: Request) -> HTMLResponse:
    return render(name="set_riddle.html", request=request)


@admin_router.get("/set-riddle/info")
async def get_riddle_info(
    url: str = Query(..., description="URL of the riddle"),
) -> schemas.BasicGameData:
    parse_logic = ParseRiddleLogic(url)
    return parse_logic.parse_riddle()


@admin_router.post("/set-riddle/check")
async def check_riddle(
    riddle: schemas.GameData, logic: RiddleLogic = Depends(get_logic)
) -> schemas.GameData:
    logic.redact(riddle)
    riddle.date = logic.get_max_riddle_date() + datetime.timedelta(days=1)
    return riddle


routers = [page_router, game_router, admin_router]
