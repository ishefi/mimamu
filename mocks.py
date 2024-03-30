from __future__ import annotations

import pprint
import random
import sys
import types
import uuid
from fnmatch import fnmatch
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from typing import TYPE_CHECKING
from unittest import TestCase
from unittest import mock

if TYPE_CHECKING:
    from typing import Any
    from typing import Collection
    from typing import Hashable
    from typing import Mapping
    from unittest.mock import Mock

    from pytest import FixtureRequest


def pp(obj: Any) -> str:
    """Format anything nicely."""
    return pprint.PrettyPrinter().pformat(obj)


class MMMTestCase(TestCase):
    """Base class for all test cases."""

    m_config: MockConfig

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


def install_loader_patcher() -> None:
    """for super mocks"""
    for loader in sys.meta_path:
        if isinstance(loader, LoaderPatcher):
            return
    sys.meta_path.insert(0, LoaderPatcher())  # type: ignore


def do_reset_global_mocks(request: FixtureRequest) -> None:
    if isinstance(request.instance, MMMTestCase):
        request.instance.m_config = MockConfig()  # new instance
        request.instance.m_config.reset()


class MockConfig(mock.MagicMock):
    instance = None  # singleton!

    def __new__(cls, *args: Any, **kwargs: Any) -> MockConfig:
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def reset(self) -> None:
        self.instance = None
        MockConfig()


class LoaderPatcher(Loader):
    """Patches `import` stations."""

    PATCHERS = {
        "common.config": MockConfig,
        # TODO: add requests
    }

    def find_spec(
        self, fullname: str, path: list[str], target: Any = None
    ) -> ModuleSpec | None:
        if any(fnmatch(fullname, p) for p in self.PATCHERS):
            return ModuleSpec(fullname, self)
        return None

    @staticmethod
    def exec_module(module: types.ModuleType) -> Any | None:
        for pattern, patcher in LoaderPatcher.PATCHERS.items():
            module_name: str = module.__name__
            if fnmatch(module_name, pattern):
                patched_module = patcher()
                sys.modules[module_name] = patched_module
                return patched_module
        return None
