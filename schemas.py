#!/usr/bin/env python
import datetime
from typing import Self
from typing import TypedDict

from pydantic import BaseModel


class BasicGameData(BaseModel):
    picture: str
    words: list[str]


class GameData(BasicGameData):
    date: datetime.date | None = None
    author: str
    dalle: int = 2


class GuessAnswer(BaseModel):
    correct_guesses: dict[int, str] = {}

    def update(self, other: Self) -> None:
        self.correct_guesses.update(other.correct_guesses)


class GameDataDict(TypedDict):
    picture: str
    words: list[str]
    date: datetime.datetime
    author: str
    dalle: int | None
