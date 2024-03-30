#!/usr/bin/env python
from __future__ import annotations

import datetime
import urllib.parse
from typing import TYPE_CHECKING

from freezegun import freeze_time
from mongomock import MongoClient

import schemas
from common import config
from logic import ParseRiddleLogic
from logic import RiddleLogic
from mocks import MMMTestCase

if TYPE_CHECKING:
    from typing import Any

    import pymongo.collection


@freeze_time("1989-12-03")
class TestRiddleLogic(MMMTestCase):
    def setUp(self) -> None:
        self.riddles: pymongo.collection.Collection[Any] = MongoClient().MiMaMu.riddles
        self.datetime = datetime.datetime.utcnow()  # from freezegun
        self.date = self.datetime.date()
        self.m_requests = self.patch("logic.requests")
        self.testee = RiddleLogic(
            mongo_riddles={"en": self.riddles}, lang="en", date=self.date
        )

    def tearDown(self) -> None:
        RiddleLogic._all_riddle_cache.clear()

    def _mk_riddle(
        self, date: datetime.datetime | None = None, riddle_str: str | None = None
    ) -> dict[str, datetime.datetime | str | list[str]]:
        if riddle_str is None:
            words = [self.unique_az(length=5) for _ in range(5)]
        else:
            words = riddle_str.split()
        if date is None:
            date = self.datetime
        return {
            "date": date,
            "picture": self.unique("https://pic.com/s/"),
            "words": words,
            "author": self.unique("Author"),
        }

    def test_get_riddle_for_date(self) -> None:
        # arrange
        mongo_riddle = self._mk_riddle()
        self.riddles.insert_one(mongo_riddle)

        # act
        riddle = self.testee.get_riddle_for_date(self.datetime)

        # assert
        self.assert_contains_key_value(mongo_riddle, "picture", riddle.picture)
        self.assert_contains_key_value(mongo_riddle, "words", riddle.words)
        self.assert_contains_key_value(mongo_riddle, "author", riddle.author)

    def test_get_riddle_for_date__from_cache(self) -> None:
        # arrange
        mongo_riddle = self._mk_riddle()
        self.riddles.insert_one(mongo_riddle)
        cached = self.testee.get_riddle_for_date(self.datetime)
        new_riddle = self._mk_riddle()
        self.riddles.update_one({"_id": mongo_riddle["_id"]}, {"$set": new_riddle})

        # act
        riddle = self.testee.get_riddle_for_date(self.datetime)

        # assert
        self.assertEqual(cached, riddle)

    def test_redact(self) -> None:
        # arrange
        self._mk_riddle()

        to_redact = schemas.GameData.model_validate(
            self._mk_riddle(riddle_str="I am happy")
        )

        # act
        self.testee.redact(to_redact)

        # assert
        self.assertEqual(" ".join(to_redact.words), "I am █████")

    def test_redact__punctuation(self) -> None:
        # arrange
        self._mk_riddle()
        to_redact = schemas.GameData.model_validate(
            self._mk_riddle(riddle_str="I am happy , happy")
        )

        # act
        self.testee.redact(to_redact)

        # assert
        self.assertEqual(" ".join(to_redact.words), "I am █████ , █████")

    def test_get_riddle__alert_on_not_many_riddles_left(self) -> None:
        # arrange
        newest_riddle = self._mk_riddle(
            date=self.testee.date + datetime.timedelta(days=2)
        )
        today_riddle = self._mk_riddle(date=self.testee.date)
        self.riddles.insert_many([newest_riddle, today_riddle])

        # act
        self.testee.get_riddle_for_date(self.testee.date)

        # assert
        self.m_requests.post.assert_called_once_with(
            config.alerts_webhook,  # TODO: use mock config
            json={"text": "MiMaMu Alert: Only 2 days left for 'en'!"},
        )

    def test_get_riddle__do_not_alert_if_enough_days_left(self) -> None:
        # arrange
        newest_riddle = self._mk_riddle(
            date=self.testee.date + datetime.timedelta(days=4)
        )
        today_riddle = self._mk_riddle(date=self.testee.date)
        self.riddles.insert_many([newest_riddle, today_riddle])

        # act
        self.testee.get_riddle_for_date(self.testee.date)

        # assert
        self.m_requests.post.assert_not_called()

    def test_get_riddle__do_not_alert_if_not_getting_todays_riddle(self) -> None:
        # arrange
        newest_riddle = self._mk_riddle(
            date=self.testee.date + datetime.timedelta(days=2)
        )
        tomorrow_riddle = self._mk_riddle(
            date=self.testee.date + datetime.timedelta(days=1)
        )
        today_riddle = self._mk_riddle(date=self.testee.date)
        self.riddles.insert_many([newest_riddle, tomorrow_riddle, today_riddle])

        # act
        self.testee.get_riddle_for_date(self.testee.date + datetime.timedelta(days=1))

        # assert
        self.m_requests.post.assert_not_called()


class TestParseRiddleLogic(MMMTestCase):
    def setUp(self) -> None:
        self.m_requests = self.patch("logic.requests")
        self.image_id_prefix = self.unique("prefix")
        self.image_id = f"{self.image_id_prefix}.{self.unique('suffix')}"
        self.prompt = "a group of pregnant witches doing pilates"
        self.some_uuid = self.unique("uuid")
        self.image_id_in_url = urllib.parse.quote(self.image_id)
        self.url = f"https://www.bing.com/images/create/prompt/{self.some_uuid}?id={self.image_id_in_url}"
        self.testee = ParseRiddleLogic(url=self.url)

    def _mk_bing_response(
        self, image_id: str, prompt: str | None = None, sicid: str = "blah.blah"
    ) -> dict[str, str]:
        return {
            "imageId": image_id,
            "contentUrl": self.unique("https://pic.com/s/"),
            "name": prompt if prompt is not None else self.prompt,
            "sicid": sicid,
        }

    def _assert_fetched_image_data(self) -> None:
        fetch_image_data_url = f"https://www.bing.com/images/create/detail/async/{self.some_uuid}?imageId={self.image_id_in_url}"
        self.m_requests.get.assert_called_once_with(fetch_image_data_url)

    def test_parse_riddle__bing(self) -> None:
        # arrange
        relevant_response = self._mk_bing_response(image_id=self.image_id)
        expected_image_url = relevant_response["contentUrl"]

        self.m_requests.get.return_value.json.return_value = {
            "iusn": False,
            "totalEstimatedMatches": 3,
            "value": [
                self._mk_bing_response(image_id=self.unique("irrelevant1")),
                relevant_response,
                self._mk_bing_response(image_id=self.unique("irrelevant2")),
            ],
        }

        # act
        parsed = self.testee.parse_riddle()

        # assert
        self._assert_fetched_image_data()
        self.assertEqual(parsed.picture, expected_image_url)
        self.assertEqual(
            parsed.words,
            ["a", "group", "of", "pregnant", "witches", "doing", "pilates"],
        )

    def test_parse_riddle__bing__detect_image_from_sicid(self) -> None:
        # arrange
        relevant_response = self._mk_bing_response(
            image_id=self.unique("irrelevant-by-id"),
            sicid=f"{self.image_id_prefix}.{self.unique('sicid')}",
        )
        expected_image_url = relevant_response["contentUrl"]
        self.m_requests.get.return_value.json.return_value = {
            "iusn": False,
            "totalEstimatedMatches": 3,
            "value": [
                self._mk_bing_response(image_id=self.unique("irrelevant1")),
                relevant_response,
                self._mk_bing_response(image_id=self.unique("irrelevant2")),
            ],
        }

        # act
        parsed = self.testee.parse_riddle()

        # assert
        self._assert_fetched_image_data()
        self.assertEqual(parsed.picture, expected_image_url)
        self.assertEqual(
            parsed.words,
            ["a", "group", "of", "pregnant", "witches", "doing", "pilates"],
        )
