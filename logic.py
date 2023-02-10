#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING

import schemas
import datetime

if TYPE_CHECKING:
    from pymongo.collection import Collection


class RiddleLogic:
    _riddle_cache: dict[datetime.date, schemas.GameData] = {}
    PUNCTUATION = ","
    PROMPT_KEYWORDS = ("digital", "art", "pop")

    def __init__(self, mongo_riddles: Collection, date: datetime.date):
        self.mongo_riddles = mongo_riddles
        self.date = datetime.datetime(date.year, date.month, date.day)
        self._stopwords = None

    @property
    def stopwords(self):
        if self._stopwords is None:
            with open("stopwords.txt") as stopwords:
                self._stopwords = stopwords.read().split(",")
                self._stopwords.extend(self.PUNCTUATION)
                self._stopwords.extend(self.PROMPT_KEYWORDS)
        return self._stopwords

    def get_redacted_riddle(self) -> schemas.GameData:
        riddle = self.get_riddle()
        self.redact(riddle)
        return riddle

    def redact(self, riddle: schemas.GameData) -> None:
        for i, word in enumerate(riddle.words):
            if word.lower() not in self.stopwords:
                riddle.words[i] = "█" * len(word)

    def get_riddle(self) -> schemas.GameData | None:
        if self.date not in self._riddle_cache:
            riddle = self.mongo_riddles.find_one(
                {"date": self.date}, {"date": 0, "_id": 0}
            )
            if riddle is None:
                return None
            self._riddle_cache[self.date] = schemas.GameData(**riddle)
        return self._riddle_cache[self.date].copy(deep=True)

    def set_riddle(self, riddle: schemas.GameData, force=False):
        if not force and (existing_riddle := self.get_riddle()):
            raise ValueError(f"There is a riddle for this date: {existing_riddle}")
        else:
            new_riddle = {"date": self.date}
            new_riddle.update(riddle.dict())
            self.mongo_riddles.update_one(
                {"date": self.date}, {"$set": new_riddle}, upsert=True
            )

    def guess(self, guess_word):
        for punctuation in self.PUNCTUATION:
            guess_word = guess_word.replace(punctuation, "")
        riddle = self.get_riddle()
        found_indices = {}
        for i, word in enumerate(riddle.words):
            if guess_word.lower() == word.lower():
                found_indices[i] = word
        return schemas.GuessAnswer(correct_guesses=found_indices)

    def clear_cache(self):
        self._riddle_cache.clear()
