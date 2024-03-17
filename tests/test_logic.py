#!/usr/bin/env python
from __future__ import annotations

import random
from typing import TYPE_CHECKING

import datetime
import pprint
from unittest import TestCase
from unittest import mock
import uuid

from mongomock import MongoClient
from freezegun import freeze_time

from common import config
from logic import RiddleLogic
import schemas

if TYPE_CHECKING:
    import pymongo.collection
    from unittest.mock import Mock
    from typing import Any
    from typing import Collection
    from typing import Hashable
    from typing import Mapping


def pp(obj: Any) -> str:
    """Format anything nicely."""
    return pprint.PrettyPrinter().pformat(obj)


@freeze_time("1989-12-03")
class TestRiddleLogic(TestCase):
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

    def unique(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:6]}"

    def unique_az(self, length: int) -> str:
        az = "abcdefghijklmnopqrstuvwxyz"
        return "".join(random.choices(az, k=length))

    def patch(self, name: str, *args: Any, **kwargs: Any) -> Mock:
        if not args:
            if "autospec" not in kwargs:
                if "spec" not in kwargs:
                    kwargs["autospec"] = True
        patcher = mock.patch(name, *args, **kwargs)
        mocker: Mock = patcher.start()
        self.addCleanup(lambda p: p.stop(), patcher)
        return mocker

    def assert_contains(self, haystack: Collection[Any], needle: Any) -> Any | None:
        self.assertIsNotNone(haystack)
        self.assertIn(needle, haystack)
        if isinstance(haystack, dict):
            return haystack[needle]
        else:
            return None

    def assert_contains_key_value(
        self, haystack: Mapping[Any, Any], key: Hashable, value: Any
    ) -> None:
        self.assertIsNotNone(haystack)
        actual = self.assert_contains(haystack, key)
        self.assertEqual(
            value,
            actual,
            msg=f'Expected dict["{key}"] to be {pp(value)}, got {pp(actual)}. Dict is: {pp(haystack)}',
        )

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
        newest_riddle = self._mk_riddle(date=self.testee.date + datetime.timedelta(days=2))
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
        newest_riddle = self._mk_riddle(date=self.testee.date + datetime.timedelta(days=4))
        today_riddle = self._mk_riddle(date=self.testee.date)
        self.riddles.insert_many([newest_riddle, today_riddle])

        # act
        self.testee.get_riddle_for_date(self.testee.date)

        # assert
        self.m_requests.post.assert_not_called()

    def test_get_riddle__do_not_alert_if_not_getting_todays_riddle(self) -> None:
        # arrange
        newest_riddle = self._mk_riddle(date=self.testee.date + datetime.timedelta(days=2))
        tomorrow_riddle = self._mk_riddle(date=self.testee.date + datetime.timedelta(days=1))
        today_riddle = self._mk_riddle(date=self.testee.date)
        self.riddles.insert_many([newest_riddle, tomorrow_riddle, today_riddle])

        # act
        self.testee.get_riddle_for_date(self.testee.date + datetime.timedelta(days=1))

        # assert
        self.m_requests.post.assert_not_called()
