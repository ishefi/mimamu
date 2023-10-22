#!/usr/bin/env python
from __future__ import annotations

from typing import TYPE_CHECKING

from pymongo import MongoClient
from common import config


if TYPE_CHECKING:
    import pymongo.collection


def get_mongo() -> dict[str, pymongo.collection.Collection]:
    db: pymongo.collection.Database = MongoClient(config.mongo).MiMaMu
    return {
        "en": db.riddles,
        "he": db.hebrew_riddles,
    }
