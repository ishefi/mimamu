#!/usr/bin/env python
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from datetime import datetime
from datetime import timedelta
import os
import sys

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([base])

from session import get_mongo
from logic import RiddleLogic
import schemas


def valid_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ArgumentTypeError("Bad date: should be of the format YYYY-mm-dd")


def get_date(mongo):
    cursor = mongo.find({"date": {"$exists": 1}})
    cursor = cursor.sort("date", -1)
    latest = cursor.next()
    date = latest["date"]
    dt = date + timedelta(days=1)
    print(f"Now doing {dt}", file=sys.stderr)
    return dt


def main():
    parser = ArgumentParser("Set riddle")
    parser.add_argument(
            '-u',
            '--url',
            metavar='URL',
            help="Picture URL",
            required=True
        )
    parser.add_argument(
        '-d', '--date', metavar='DATE', type=valid_date,
        help="Date of secret. If not provided, first date w/o riddle is used"
    )
    parser.add_argument("-p", '--prompt', metavar="PROMPT", help="Riddle's prompt", required=True)

    args = parser.parse_args()

    mongo = get_mongo()
    if args.date:
        date = args.date
    else:
        date = get_date(mongo)
    print(f"doing {date}")
    logic = RiddleLogic(mongo_riddles=mongo, date=date)
    logic.set_riddle(schemas.GameData(picture=args.url, words=args.prompt.split()))
    print("done")

if __name__ == "__main__":
    main()
