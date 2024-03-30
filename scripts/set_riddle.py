#!/usr/bin/env python
from __future__ import annotations

import datetime
import os
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from typing import TYPE_CHECKING

from PIL import Image

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([base])

import schemas  # noqa: E402
from logic import ParseRiddleLogic  # noqa: E402
from logic import RiddleLogic  # noqa: E402
from session import get_mongo  # noqa: E402

if TYPE_CHECKING:
    from typing import Literal


def main() -> None:
    parser = ArgumentParser("Set riddle")
    parser.add_argument(
        dest="url",
        metavar="URL",
        help="Shared DALL·E {2|3} URL",
    )
    parser.add_argument(
        "-l",
        "--lang",
        metavar="LANG",
        help="Language to set riddle for",
        choices=["he", "en"],
        required=True,
    )
    parser.add_argument(
        "-d",
        "--date",
        metavar="DATE",
        type=datetime.date.fromisoformat,
        help="Date of secret. If not provided, first date w/o riddle is used",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Skip repeat-checks etc."
    )

    args = parser.parse_args()

    mongo = get_mongo()
    if args.date:
        date = args.date
    else:
        date = RiddleLogic(
            mongo_riddles=mongo, lang=args.lang, date=datetime.datetime.today()
        ).get_max_riddle_date()
    url = args.url
    print(f"doing {date}")
    while url:
        parse_logic = ParseRiddleLogic(url=url)
        basic_riddle = parse_logic.parse_riddle()
        author = input("Author? > ")
        urllib.request.urlretrieve(basic_riddle.picture, "tmp.png")
        with Image.open("tmp.png") as img:
            img.show()
        riddle = schemas.GameData(
            picture=basic_riddle.picture,
            words=basic_riddle.words,
            author=author,
            dalle=3,
        )
        logic = RiddleLogic(mongo_riddles=mongo, date=date, lang=args.lang)
        _approve_riddle(logic, riddle, args.force, args.lang)
        logic.get_first_riddle_date()
        date = logic.get_max_riddle_date() + datetime.timedelta(days=1)
        url = input(f"doing {date}\nNew URL > ")
    print("done")


def _approve_riddle(
    logic: RiddleLogic,
    riddle: schemas.GameData,
    force: bool,
    lang: Literal["en", "he"],
) -> None:
    redacted = riddle.copy(deep=True)
    logic.redact(redacted)
    prompt = " ".join(riddle.words)
    print(f"{riddle.author}'s Prompt: {prompt if lang == 'en' else prompt[::-1]}")
    if lang == "he":
        redacted_words = " ".join([word[::-1] for word in redacted.words[::-1]])
    else:
        redacted_words = " ".join(redacted.words)
    print(f"Redacted: {redacted_words}")
    is_ok = input("Is ok? [cyN] ")
    if is_ok in ["y", "Y"]:
        logic.set_riddle(riddle, force=force)
    elif is_ok in ["c", "C"]:
        new_prompt = input("new prompt words? ")
        riddle = schemas.GameData(
            picture=riddle.picture,
            words=new_prompt.replace("-", " ").split(),
            author=riddle.author,
        )
        _approve_riddle(logic, riddle, force, lang)


if __name__ == "__main__":
    main()
