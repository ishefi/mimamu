#!/usr/bin/env python
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from logic import RiddleLogic
import schemas

templates = Jinja2Templates(directory="templates")
page_router = APIRouter()
game_router = APIRouter(prefix="/game")


@page_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        context={
            "request": request,
        },
    )


@game_router.get("/data")
async def get_game(request: Request) -> schemas.GameData:
    logic = RiddleLogic(
        mongo_riddles=request.app.state.mongo, date=request.app.state.date
    )
    return logic.get_redacted_riddle()


@game_router.get("/guess")
async def guess(request: Request, guess_word: str) -> schemas.GuessAnswer:
    guess_word = guess_word.split()
    logic = RiddleLogic(
        mongo_riddles=request.app.state.mongo, date=request.app.state.date
    )
    guess_answer = schemas.GuessAnswer()
    for word in guess_word:
        guess_answer.update(logic.guess(word.strip()))
    return guess_answer


routers = [page_router, game_router]
