#!/usr/bin/env python
from __future__ import annotations

import datetime
from collections import defaultdict
from typing import TYPE_CHECKING

import requests

import schemas
import stopwords
from common import config
from common.errors import MMMError

if TYPE_CHECKING:
    from typing import Any

    import pymongo.collection


class RiddleLogic:
    _all_riddle_cache: dict[str, dict[datetime.date, schemas.GameData]] = defaultdict(
        dict
    )
    PAGE_SIZE = 6

    def __init__(
        self,
        mongo_riddles: dict[str, pymongo.collection.Collection[Any]],
        date: datetime.date,
        lang: str,
    ):
        self.all_mongo_riddles = mongo_riddles
        self.date = datetime.datetime(date.year, date.month, date.day)
        self.stopwords = stopwords.all_stopwords[lang]
        self.lang = lang

    @property
    def mongo_riddles(self) -> pymongo.collection.Collection[Any]:
        return self.all_mongo_riddles[self.lang]

    @property
    def riddle_cache(self) -> dict[datetime.date, schemas.GameData]:
        return self._all_riddle_cache[self.lang]

    def get_redacted_riddle(self) -> schemas.GameData:
        riddle = self.get_riddle_for_date(self.date)
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

    def get_riddle_for_date(self, date: datetime.datetime) -> schemas.GameData:
        if date not in self.riddle_cache:
            if date == self.date:
                self._check_max()
            riddle = self.mongo_riddles.find_one({"date": date}, {"_id": 0})
            if riddle is None:
                raise MMMError(45383, f"No riddle found for date {date.date()}")
            self.riddle_cache[date] = schemas.GameData(**riddle)
        return self.riddle_cache[date].model_copy(deep=True)

    def _check_max(self) -> None:
        max_riddle = self.mongo_riddles.find_one({}, sort=[("date", -1)])
        if max_riddle is None:
            raise MMMError(message="Error finding riddle", code=464353)
        time_left = max_riddle["date"].date() - datetime.datetime.utcnow().date()
        if (left := time_left.days) <= 3:
            requests.post(
                config.alerts_webhook,
                json={
                    "text": f"MiMaMu Alert: Only {left} days left for '{self.lang}'!"
                },
            )

    def set_riddle(self, riddle: schemas.GameData, force: bool = False) -> None:
        if not force:
            try:
                existing_riddle = self.get_riddle_for_date(self.date)
                raise ValueError(f"There is a riddle for this date: {existing_riddle}")
            except MMMError:
                pass
        new_riddle = riddle.dict()
        new_riddle.update({"date": self.date})
        self.mongo_riddles.update_one(
            {"date": self.date}, {"$set": new_riddle}, upsert=True
        )

    def guess(self, guess_word: str) -> schemas.GuessAnswer:
        for punctuation in stopwords.punctuation:
            guess_word = guess_word.replace(punctuation, "")
        riddle = self.get_riddle_for_date(self.date)
        found_indices = {}
        for i, word in enumerate(riddle.words):
            if guess_word.lower() == word.lower():
                found_indices[i] = word
        return schemas.GuessAnswer(correct_guesses=found_indices)

    def get_history(self, page: int) -> list[schemas.GameData]:
        riddle_history = []
        for day in range(self.PAGE_SIZE):
            historia_date = self.date - datetime.timedelta(
                days=1 + (page * self.PAGE_SIZE + day)
            )
            if historia_date < self.get_first_riddle_date():
                continue
            riddle_history.append(self.get_riddle_for_date(historia_date))
        return riddle_history

    def clear_cache(self) -> None:
        self._all_riddle_cache.clear()

    def get_first_riddle_date(self) -> datetime.datetime:
        # TODO: cache this
        first_riddle = self.mongo_riddles.find_one({}, sort=[("date", 1)])
        if first_riddle is None:
            raise MMMError(message="Error finding riddles", code=63456)
        first_date: datetime.datetime = first_riddle["date"]
        return first_date
