#!/usr/bin/env python
import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi import status

from auth import verify_token
from logic import RiddleLogic
import schemas

templates = Jinja2Templates(directory="templates")
page_router = APIRouter()
game_router = APIRouter(prefix="/game")
admin_router = APIRouter(prefix="/admin", dependencies=[Depends(verify_token)])


def render(name: str, request, **kwargs):
    kwargs['js_version'] = request.app.state.js_version
    kwargs['css_version'] = request.app.state.css_version
    kwargs['request'] = request
    return templates.TemplateResponse(
        name,
        context=kwargs
    )


@page_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return render(name="index.html", request=request)


@page_router.get("/history", response_class=HTMLResponse, include_in_schema=False)
async def history(request: Request):
    return render(name="history.html", request=request)


def get_logic(request: Request):
    days_delta = datetime.timedelta(days=request.app.state.date_delta)
    date = datetime.datetime.today().date() + days_delta
    return RiddleLogic(mongo_riddles=request.app.state.mongo, date=date)


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
async def get_puzzle_version(request: Request) -> dict:
    return {"version": request.app.state.puzzle_version}


@game_router.get("/history")
async def get_history(page: int, logic: RiddleLogic = Depends(get_logic)) -> list[schemas.GameData]:
    return logic.get_history(page)


@admin_router.delete("/cache", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cache(logic: RiddleLogic = Depends(get_logic)) -> None:
    logic.clear_cache()


routers = [page_router, game_router, admin_router]
