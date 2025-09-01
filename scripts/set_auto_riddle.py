#!/usr/bin/env python
from __future__ import annotations

import datetime
import os
import sys
from argparse import ArgumentParser

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([base])

from logic import RiddleLogic  # noqa: E402
from session import get_mongo  # noqa: E402


def main() -> None:
    parser = ArgumentParser("Set riddle")
    parser.add_argument("--max-date", type=datetime.date.fromisoformat, required=True)
    args = parser.parse_args()

    mongo = get_mongo()
    riddle_logic = RiddleLogic(
        mongo_riddles=mongo, lang="en", date=datetime.datetime.today()
    )
    max_riddle_date = riddle_logic.get_max_riddle_date()
    max_riddle_datetime = datetime.datetime(
        year=max_riddle_date.year, month=max_riddle_date.month, day=max_riddle_date.day
    )
    yesteriddle = " ".join(riddle_logic.get_riddle_for_date(max_riddle_datetime).words)

    next_riddle_date = riddle_logic.get_max_riddle_date() + datetime.timedelta(days=1)
    print(f"Current next_riddle_date: {next_riddle_date}", file=sys.stderr)

    while next_riddle_date < args.max_date:
        print(f"doing {next_riddle_date}", file=sys.stderr)
        riddle_logic = RiddleLogic(
            mongo_riddles=mongo, lang="en", date=next_riddle_date
        )
        try:
            yesteriddle = " ".join(
                riddle_logic.auto_generate_riddle(yesteriddle=yesteriddle).words
            )
        except Exception as e:
            print("Error generating riddle", file=sys.stderr)
            with open("error.log", "w") as log_file:
                print(f"Error on date: {next_riddle_date} - {str(e)}", file=log_file)
            exit(1)
        next_riddle_date += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
