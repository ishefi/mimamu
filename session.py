#!/usr/bin/env python
from __future__ import annotations

from typing import TYPE_CHECKING

from pymongo import MongoClient

import schemas
from common import config

if TYPE_CHECKING:
    from typing import Any

    import pymongo.collection
    import pymongo.database


def get_mongo() -> dict[str, pymongo.collection.Collection[schemas.GameDataDict]]:
    db: pymongo.database.Database[Any] = MongoClient(config.mongo).MiMaMu
    return {
        "en": db.riddles,
        "he": db.hebrew_riddles,
    }
