#!/usr/bin/env python
from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup
from PIL import Image

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([base])

import schemas  # noqa: E402
import stopwords  # noqa: E402
from logic import ParseRiddleLogic  # noqa: E402
from logic import RiddleLogic  # noqa: E402
from session import get_mongo  # noqa: E402

if TYPE_CHECKING:
    from typing import Any
    from typing import Literal

    import pymongo.collection

DALLE_AUTHOR = " × DALL·E | "


def valid_date(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ArgumentTypeError("Bad date: should be of the format YYYY-mm-dd")


def get_date(mongo: pymongo.collection.Collection[Any]) -> datetime:
    cursor = mongo.find({"date": {"$exists": 1}})
    cursor = cursor.sort("date", -1)
    latest = cursor.next()
    date: datetime = latest["date"]
    dt = date + timedelta(days=1)
    return dt


def get_dalle_2(url: str) -> tuple[schemas.BasicGameData, str]:
    dalle_page = requests.get(url)
    html = BeautifulSoup(dalle_page.text, features="html.parser")
    if html.title is None:
        raise ValueError("Invalid page title, check URL")
    raw_prompt = html.title.text
    author, prompt = raw_prompt.split(DALLE_AUTHOR)
    (meta_image,) = html.find_all("meta", property="og:image")
    image_url = meta_image.get("content")
    prompt = prompt.replace("-", " ")
    for punct in stopwords.punctuation:
        prompt = prompt.replace(punct, f" {punct} ")
    prompt_words = prompt.strip().split()
    basic_riddle = schemas.BasicGameData(picture=image_url, words=prompt_words)
    return basic_riddle, author


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
        type=valid_date,
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
        date = get_date(mongo[args.lang])
    url = args.url
    print(f"doing {date}")
    while url:
        if "bing" in url.lower():
            parse_logic = ParseRiddleLogic(url=url)
            basic_riddle = parse_logic.parse_riddle()
            author = input("Author? > ")
            dalle = 3
        else:
            basic_riddle, author = get_dalle_2(url)
            dalle = 2
        urllib.request.urlretrieve(basic_riddle.picture, "tmp.png")
        with Image.open("tmp.png") as img:
            img.show()
        riddle = schemas.GameData(
            picture=basic_riddle.picture,
            words=basic_riddle.words,
            author=author,
            dalle=dalle,
        )
        logic = RiddleLogic(mongo_riddles=mongo, date=date, lang=args.lang)
        _approve_riddle(logic, riddle, args.force, args.lang)
        date = get_date(mongo[args.lang])
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
