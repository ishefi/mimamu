#!/usr/bin/env python
from __future__ import annotations

import datetime
import re
import urllib.parse
from collections import defaultdict
from typing import TYPE_CHECKING

import openai
import requests

import schemas
import stopwords
from common import config
from common.errors import MMMError

if TYPE_CHECKING:
    import pymongo.collection


class RiddleLogic:
    _all_riddle_cache: dict[str, dict[datetime.date, schemas.GameData]] = defaultdict(
        dict
    )
    PAGE_SIZE = 9

    def __init__(
        self,
        mongo_riddles: dict[str, pymongo.collection.Collection[schemas.GameDataDict]],
        date: datetime.date,
        lang: str,
    ):
        self.all_mongo_riddles = mongo_riddles
        self.date = datetime.datetime(date.year, date.month, date.day)
        self.stopwords = stopwords.all_stopwords[lang]
        self.lang = lang

    @property
    def mongo_riddles(self) -> pymongo.collection.Collection[schemas.GameDataDict]:
        return self.all_mongo_riddles[self.lang]

    @property
    def riddle_cache(self) -> dict[datetime.date, schemas.GameData]:
        return self._all_riddle_cache[self.lang]

    def get_redacted_riddle(self, with_pic: bool = True) -> schemas.GameData:
        riddle = self.get_riddle_for_date(self.date, with_pic=with_pic)
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

    def get_riddle_for_date(
        self, date: datetime.datetime, with_pic: bool = True
    ) -> schemas.GameData:
        if date not in self.riddle_cache:
            if date == self.date:
                self._check_max()
            projection = {"_id": 0}
            if not with_pic:
                projection["picture"] = 0
            riddle = self.mongo_riddles.find_one({"date": date}, projection)
            if riddle is None:
                raise MMMError(45383, f"No riddle found for date {date.date()}")
            game_data = schemas.GameData(
                picture=riddle.get("picture"),
                words=riddle["words"],
                date=riddle["date"],
                author=riddle["author"],
                dalle=riddle["dalle"] or 2,
            )
            if with_pic:
                self.riddle_cache[date] = game_data
            else:
                return game_data
        return self.riddle_cache[date].model_copy(deep=True)

    def get_riddle_for_date_range(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> list[schemas.GameData]:
        date_filters = []
        data_to_return = []
        for date in range((end - start).days + 1):
            if (
                date_date := start + datetime.timedelta(days=date)
            ) in self.riddle_cache:
                data_to_return.append(
                    self.riddle_cache[date_date].model_copy(deep=True)
                )
            else:
                date_filters.append(date_date)
        if date_filters:
            for riddle in self.mongo_riddles.find(
                {"date": {"$in": date_filters}}, {"_id": 0}
            ):
                self.riddle_cache[riddle["date"]] = schemas.GameData(**riddle)
                data_to_return.append(schemas.GameData(**riddle))
        data_to_return.sort(key=lambda x: x.date, reverse=True)  # type: ignore
        return data_to_return

    def _check_max(self) -> None:
        max_riddle_date = self.get_max_riddle_date()
        time_left = max_riddle_date - datetime.datetime.utcnow().date()
        if (left := time_left.days) <= 3:
            requests.post(
                config.alerts_webhook,
                json={
                    "text": f"MiMaMu Alert: Only {left} days left for '{self.lang}'!"
                },
            )

    def get_max_riddle_date(self) -> datetime.date:
        max_riddle = self.mongo_riddles.find_one({}, sort=[("date", -1)])
        if max_riddle is None:
            raise MMMError(message="Error finding riddle", code=464353)
        riddle_date: datetime.datetime = max_riddle["date"]
        return riddle_date.date()

    def set_riddle(self, riddle: schemas.GameData, force: bool) -> None:
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
        if page < 0:
            max_date = self.get_max_riddle_date()
            first_historia_date = datetime.datetime(
                max_date.year, max_date.month, max_date.day
            )
            last_historia_date = self.date
        else:
            first_historia_date = self.date - datetime.timedelta(
                days=1 + page * self.PAGE_SIZE
            )
            last_historia_date = first_historia_date - datetime.timedelta(
                days=self.PAGE_SIZE - 1
            )
        return self.get_riddle_for_date_range(last_historia_date, first_historia_date)

    def clear_cache(self) -> None:
        self._all_riddle_cache.clear()

    def get_first_riddle_date(self) -> datetime.datetime:
        # TODO: cache this
        first_riddle = self.mongo_riddles.find_one({}, sort=[("date", 1)])
        if first_riddle is None:
            raise MMMError(message="Error finding riddles", code=63456)
        first_date: datetime.datetime = first_riddle["date"]
        return first_date

    def auto_generate_riddle(self, force: bool = False) -> None:
        client = openai.OpenAI(api_key=config.openai_api_key)

        # 1. Generate a creative/absurd image description (prompt)
        # using OpenAI Chat Completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative AI that invents absurd, funny, or "
                    "surreal image descriptions for a daily riddle game. Each "
                    "description should be a single sentence, 10-15 words, vivid, "
                    "and suitable for generating an image. Do not include anything in "
                    "your answer, just the description.",
                },
                {
                    "role": "user",
                    "content": "Generate a new, unique, and absurd image description "
                    "for today's riddle.",
                },
            ],
            max_tokens=60,
            temperature=1.2,
        )
        prompt = response.choices[0].message.content
        assert isinstance(prompt, str)
        # 2. Generate an image using DALL·E (OpenAI Image API)
        image_response = client.images.generate(
            prompt=prompt.strip(),
            response_format="b64_json",
            n=1,
            model="dall-e-3",
            size="1024x1024",
        )
        assert image_response.data is not None
        base64_image = image_response.data[0].b64_json
        assert isinstance(base64_image, str)
        last_riddle_date = self.get_max_riddle_date()
        riddle_data = schemas.GameData(
            picture=base64_image,
            words=prompt.split(),
            date=last_riddle_date + datetime.timedelta(days=1),
            author="Auto (OpenAI)",
            dalle=3,
        )
        self.set_riddle(riddle_data, force=force)


class ParseRiddleLogic:
    PARSE_URL_RE = re.compile(r"/create/.*/")

    def __init__(self, url: str):
        self.url = url

    def parse_riddle(self) -> schemas.BasicGameData:
        parsed_path, image_id, image_id_prefix = self._parse_url()
        prompt, image_url = self._fetch_image_data(
            parsed_path, image_id, image_id_prefix
        )
        return schemas.BasicGameData(
            picture=image_url, words=self._parse_prompt(prompt)
        )

    def _parse_url(self) -> tuple[str, str, str]:
        url = self.PARSE_URL_RE.sub("/create/detail/async/", self.url)
        parsed = urllib.parse.urlparse(url)
        parsed_query = urllib.parse.parse_qs(parsed.query)
        (image_id,) = parsed_query["id"]
        image_id_prefix = image_id.split(".")[0]
        return parsed.path, image_id, image_id_prefix

    @staticmethod
    def _fetch_image_data(
        parsed_path: str, image_id: str, image_id_prefix: str
    ) -> tuple[str, str]:
        query = urllib.parse.urlencode({"imageId": image_id})
        newrl = f"https://www.bing.com{parsed_path}?{query}"
        headers = {
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
            )
        }
        images = requests.get(newrl, headers=headers).json()
        for data in images["value"]:
            if data["imageId"] == image_id or data["sicid"].startswith(image_id_prefix):
                return data["name"], data["contentUrl"]
        raise MMMError(code=624532, message=f"Image data not found for {image_id}")

    @staticmethod
    def _parse_prompt(prompt: str) -> list[str]:
        prompt = prompt.replace("-", " ")
        for punct in stopwords.punctuation:
            prompt = prompt.replace(punct, f" {punct} ")
        return prompt.strip().split()
