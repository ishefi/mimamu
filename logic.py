#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING

from common import config
from common.errors import MMMError
import schemas
import datetime

import stopwords

if TYPE_CHECKING:
    import pymongo.collection


class RiddleLogic:
    _riddle_cache: dict[datetime.date, schemas.GameData] = {}
    PAGE_SIZE = 6

    def __init__(
        self, mongo_riddles: pymongo.collection.Collection, date: datetime.date
    ):
        self.mongo_riddles = mongo_riddles
        self.date = datetime.datetime(date.year, date.month, date.day)
        self.stopwords = stopwords.all_stopwords
        self.first_game_date = datetime.datetime.strptime(config.first_game_date, "%Y-%m-%d")

    def get_redacted_riddle(self) -> schemas.GameData:
        riddle = self.get_riddle()
        self.redact(riddle)
        return riddle

    def _should_redact(self, word: str) -> bool:
        if word.lower() in self.stopwords:
            return False
        if not word.isalpha():
            return False
        return True

    def redact(self, riddle: schemas.GameData) -> None:
        for i, word in enumerate(riddle.words):
            if self._should_redact(word):
                riddle.words[i] = "█" * len(word)

    def get_riddle(self, date=None) -> schemas.GameData:
        if date is None:
            date = self.date
        if date not in self._riddle_cache:
            riddle = self.mongo_riddles.find_one(
                {"date": date}, {"_id": 0}
            )
            if riddle is None:
                raise MMMError(45383, f"No riddle found for date {date.date()}")
            self._riddle_cache[date] = schemas.GameData(**riddle)
        return self._riddle_cache[date].copy(deep=True)

    def set_riddle(self, riddle: schemas.GameData, force=False) -> None:
        if not force:
            try:
                existing_riddle = self.get_riddle()
                raise ValueError(f"There is a riddle for this date: {existing_riddle}")
            except MMMError:
                pass
        new_riddle = riddle.dict()
        new_riddle.update({"date": self.date})
        self.mongo_riddles.update_one(
            {"date": self.date}, {"$set": new_riddle}, upsert=True
        )

    def guess(self, guess_word) -> schemas.GuessAnswer:
        for punctuation in stopwords.punctuation:
            guess_word = guess_word.replace(punctuation, "")
        riddle = self.get_riddle()
        found_indices = {}
        for i, word in enumerate(riddle.words):
            if guess_word.lower() == word.lower():
                found_indices[i] = word
        return schemas.GuessAnswer(correct_guesses=found_indices)

    def get_history(self, page) -> list[schemas.GameData]:
        riddle_history = []
        for day in range(self.PAGE_SIZE):
            historia_date = self.date - datetime.timedelta(days=1 + (page * self.PAGE_SIZE + day))
            if historia_date < self.first_game_date:
                continue
            riddle_history.append(self.get_riddle(historia_date))
        return riddle_history

    def clear_cache(self) -> None:
        self._riddle_cache.clear()
