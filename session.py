#!/usr/bin/env python
from pymongo import MongoClient
from common import config


def get_mongo():
    mongdb = MongoClient(config.mongo).MiMaMu
    return mongdb.riddles
