#!/usr/bin/env python
from __future__ import annotations

from typing import TYPE_CHECKING

from pymongo import MongoClient
from common import config


if TYPE_CHECKING:
    import pymongo.collection


def get_mongo() -> pymongo.collection.Collection:
    return MongoClient(config.mongo).MiMaMu.riddles
