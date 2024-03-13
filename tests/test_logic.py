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


class TestRiddleLogic(TestCase):
    def setUp(self) -> None:
        self.riddles: pymongo.collection.Collection[Any] = MongoClient().MiMaMu.riddles
        self.datetime = datetime.datetime(1989, 12, 3)
        self.date = self.datetime.date()
        self.requests = self.patch("logic.requests")
        self.testee = RiddleLogic(
            mongo_riddles={"en": self.riddles}, lang="en", date=self.date
        )
        self.addCleanup(self.testee.clear_cache)

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
        new_riddle_dict = self._mk_riddle()
        self.riddles.update_one({"_id": mongo_riddle["_id"]}, {"$set": new_riddle_dict})
        new_riddle = schemas.GameData.model_validate(new_riddle_dict)

        # act
        riddle = self.testee.get_riddle_for_date(self.datetime)

        # assert
        self.assertEqual(cached, riddle)
        self.assertNotEqual(new_riddle, riddle)

    def test_get_riddle_for_date__after_cache_clear(self) -> None:
        # arrange
        mongo_riddle = self._mk_riddle()
        self.riddles.insert_one(mongo_riddle)
        cached = self.testee.get_riddle_for_date(self.datetime)
        new_riddle_dict = self._mk_riddle()
        self.riddles.update_one({"_id": mongo_riddle["_id"]}, {"$set": new_riddle_dict})
        new_riddle = schemas.GameData.model_validate(new_riddle_dict)

        # act
        self.testee.clear_cache()
        riddle = self.testee.get_riddle_for_date(self.datetime)

        # assert
        self.assertEqual(new_riddle, riddle)
        self.assertNotEqual(cached, riddle)

    def test_redact(self) -> None:
        # arrange
        to_redact = schemas.GameData.model_validate(
            self._mk_riddle(riddle_str="I am happy")
        )

        # act
        self.testee.redact(to_redact)

        # assert
        self.assertEqual(" ".join(to_redact.words), "I am █████")

    def test_redact__punctuation(self) -> None:
        # arrange
        to_redact = schemas.GameData.model_validate(
            self._mk_riddle(riddle_str="I am happy , happy")
        )

        # act
        self.testee.redact(to_redact)

        # assert
        self.assertEqual(" ".join(to_redact.words), "I am █████ , █████")

    def test_get_redacted_riddle(self) -> None:
        # arrange
        riddle = self._mk_riddle(riddle_str="I am happy", date=self.datetime)
        self.riddles.insert_one(riddle)

        # act
        redacted = self.testee.get_redacted_riddle()

        # assert
        self.assertEqual(redacted.words, ["I", "am", "█████"])
        self.assertEqual(redacted.picture, riddle["picture"])
        self.assertEqual(redacted.author, riddle["author"])
        self.assertEqual(redacted.dalle, 2)

    def test_dont_redact_non_alpha_word(self) -> None:
        # arrange
        to_redact = schemas.GameData.model_validate(
            self._mk_riddle(riddle_str="I am happy3")
        )

        # act
        self.testee.redact(riddle=to_redact)

        # assert
        self.assertEqual(to_redact.words, ["I", "am", "happy3"])

    def test_guess(self) -> None:
        # arrange
        riddle = self._mk_riddle()
        self.riddles.insert_one(riddle)
        riddle_words = riddle["words"]
        assert isinstance(riddle_words, list)
        guess = random.choice(riddle_words)
        guess_index = riddle_words.index(guess)

        # act
        answer = self.testee.guess(guess)

        # assert
        self.assert_contains_key_value(answer.correct_guesses, guess_index, guess)

    def test_guess_with_punctuation(self) -> None:
        # arrange
        riddle = self._mk_riddle()
        self.riddles.insert_one(riddle)
        riddle_words = riddle["words"]
        assert isinstance(riddle_words, list)
        guess = random.choice(riddle_words)
        guess_index = riddle_words.index(guess)

        # act
        answer = self.testee.guess(f"{guess}.")

        # assert
        self.assert_contains_key_value(answer.correct_guesses, guess_index, guess)

    def test_set_riddle(self) -> None:
        # arrange
        riddle = self._mk_riddle()

        # act
        self.testee.set_riddle(riddle=schemas.GameData.model_validate(riddle))

        # assert
        mongo_riddle = self.riddles.find_one(riddle)
        self.assertIsNotNone(mongo_riddle)

    def test_dont_set_riddle_if_there_is_an_existing_one_for_the_same_date(
        self,
    ) -> None:
        # arrange
        existing_riddle = self._mk_riddle()
        new_riddle = self._mk_riddle()
        self.riddles.insert_one(existing_riddle)

        # act
        with self.assertRaises(ValueError):
            self.testee.set_riddle(
                riddle=schemas.GameData.model_validate(new_riddle), force=False
            )

        # assert
        self.assertIsNotNone(self.riddles.find_one(existing_riddle))
        self.assertIsNone(self.riddles.find_one(new_riddle))

    def test_override_set_riddle_if_forced(self) -> None:
        # arrange
        existing_riddle = self._mk_riddle()
        new_riddle = self._mk_riddle()
        self.riddles.insert_one(existing_riddle)

        # act
        self.testee.set_riddle(
            riddle=schemas.GameData.model_validate(new_riddle), force=True
        )

        # assert
        self.assertIsNotNone(self.riddles.find_one(new_riddle))
        self.assertIsNone(self.riddles.find_one(existing_riddle))

    def test_get_history(self) -> None:
        # arrange
        mongo_history = [
            self._mk_riddle(date=self.datetime - datetime.timedelta(days=i))
            for i in range(10)
        ]
        self.riddles.insert_many(mongo_history)

        # act
        history = self.testee.get_history(page=0)

        # assert
        expected_history = [
            schemas.GameData.model_validate(historia)
            for historia in mongo_history[1:7]  # the first is today, page size is 6
        ]
        self.assertEqual(expected_history, history)

    def test_get_history__last_page(self) -> None:
        # arrange
        mongo_history = [
            self._mk_riddle(date=self.datetime - datetime.timedelta(days=i))
            for i in range(10)
        ]
        self.riddles.insert_many(mongo_history)

        # act
        history = self.testee.get_history(page=1)

        # assert
        expected_history = [
            schemas.GameData.model_validate(historia)
            for historia in mongo_history[7:]  # the first is today, page size is 6
        ]
        self.assertEqual(expected_history, history)
