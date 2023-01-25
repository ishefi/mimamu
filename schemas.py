#!/usr/bin/env python
from typing import Self
from pydantic import BaseModel


class GameData(BaseModel):
    picture: str
    words: list[str]


class GuessAnswer(BaseModel):
    correct_guesses: dict[int, str] = {}

    def update(self, other: Self) -> None:
        self.correct_guesses.update(other.correct_guesses)

