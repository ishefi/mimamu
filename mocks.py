from __future__ import annotations

import pprint
import random
import uuid
from typing import TYPE_CHECKING
from unittest import TestCase
from unittest import mock

if TYPE_CHECKING:
    from typing import Any
    from typing import Collection
    from typing import Hashable
    from typing import Mapping
    from unittest.mock import Mock


def pp(obj: Any) -> str:
    """Format anything nicely."""
    return pprint.PrettyPrinter().pformat(obj)


class MMMTestCase(TestCase):
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
            msg=f'Expected dict["{key}"] to be {pp(value)}, '
            f"got {pp(actual)}. Dict is: {pp(haystack)}",
        )
