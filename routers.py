#!/usr/bin/env python
import datetime

from fastapi import APIRouter, Query
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi import status

from auth import verify_token
from common import config
from logic import RiddleLogic
import schemas
from typing import Any, Annotated

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


def get_logic(request: Request) -> RiddleLogic:
    days_delta = datetime.timedelta(days=request.app.state.date_delta)
    date = datetime.datetime.utcnow().date() + days_delta
    mongo = request.app.state.mongo
    return RiddleLogic(
        mongo_riddles=mongo,
        date=date,
        lang=request.cookies.get("lang", "en"),
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


routers = [page_router, game_router, admin_router]
