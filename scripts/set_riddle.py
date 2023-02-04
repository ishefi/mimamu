#!/usr/bin/env python
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from datetime import datetime
from datetime import timedelta
import os
import sys
import urllib

from PIL import Image
from bs4 import BeautifulSoup
import requests

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([base])

from session import get_mongo
from logic import RiddleLogic
import schemas

DALLE_AUTHOR = " × DALL·E | "


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
    return dt


def main():
    parser = ArgumentParser("Set riddle")
    parser.add_argument(
            dest="url",
            metavar='URL',
            help="Shared DALL·E 2 URL",
        )
    parser.add_argument(
        '-d', '--date', metavar='DATE', type=valid_date,
        help="Date of secret. If not provided, first date w/o riddle is used"
    )

    args = parser.parse_args()

    mongo = get_mongo()
    if args.date:
        date = args.date
    else:
        date = get_date(mongo)
    url = args.url
    while url:
        print(f"doing {date}")
        dalle_page = requests.get(url)
        html = BeautifulSoup(dalle_page.text, features="html.parser")
        raw_prompt = html.title.text
        author, prompt = raw_prompt.split(DALLE_AUTHOR)
        prompt = prompt.replace(",", " ,")
        prompt_words = prompt.strip().split()
        meta_image, = html.find_all("meta", property="og:image")
        image_url = meta_image.get("content")

        urllib.request.urlretrieve(image_url, "tmp.png")
        with Image.open("tmp.png") as img:
            img.show()
        riddle = schemas.GameData(picture=image_url, words=prompt_words, author=author)
        logic = RiddleLogic(mongo_riddles=mongo, date=date)
        redacted = riddle.copy()
        logic.redact(redacted)
        print(f"{author}'s Prompt: {prompt}")
        print(f"Redacted: {' '.join(redacted.words)}")
        if input("Is ok? [yN] ") in ["y", "Y"]:
            logic.set_riddle(riddle)
            date = get_date(mongo)
        url = input("New URL > ")
    print("done")


if __name__ == "__main__":
    main()
