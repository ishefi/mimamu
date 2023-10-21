#!/usr/bin/env python
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from datetime import datetime
from datetime import timedelta
import os
import re
import sys
import urllib.request
import urllib.parse

from PIL import Image
from bs4 import BeautifulSoup
import requests

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([base])

from session import get_mongo  # noqa
from logic import RiddleLogic  # noqa
import stopwords  # noqa
import schemas  # noqa

DALLE_AUTHOR = " × DALL·E | "


def valid_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ArgumentTypeError("Bad date: should be of the format YYYY-mm-dd")


def get_date(mongo):
    cursor = mongo.find({"date": {"$exists": 1}})
    cursor = cursor.sort("date", -1)
    latest = cursor.next()
    date = latest["date"]
    dt = date + timedelta(days=1)
    return dt


def get_dalle_2(url):
    dalle_page = requests.get(url)
    html = BeautifulSoup(dalle_page.text, features="html.parser")
    if html.title is None:
        raise ValueError("Invalid page title, check URL")
    raw_prompt = html.title.text
    author, prompt = raw_prompt.split(DALLE_AUTHOR)
    (meta_image,) = html.find_all("meta", property="og:image")
    image_url = meta_image.get("content")
    return prompt, image_url, author


def get_bing(url):
    url = re.sub("/create/.*/", "/create/detail/async/", url)
    parsed = urllib.parse.urlparse(url)
    parsed_query = urllib.parse.parse_qs(parsed.query)
    (image_id,) = parsed_query["id"]
    newrl = f"https://www.bing.com{parsed.path}?{urllib.parse.urlencode({'imageId': image_id})}"
    images = requests.get(newrl).json()
    image_data = next(data for data in images["value"] if data["imageId"] == image_id)
    prompt = image_data["name"]
    image_url = image_data["contentUrl"]
    author = input("Author? > ")
    return prompt, image_url, author


def main():
    parser = ArgumentParser("Set riddle")
    parser.add_argument(
        dest="url",
        metavar="URL",
        help="Shared DALL·E {2|3} URL",
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
        date = get_date(mongo)
    url = args.url
    print(f"doing {date}")
    while url:
        if "bing" in url.lower():
            prompt, image_url, author = get_bing(url)
            dalle = 3
        else:
            prompt, image_url, author = get_dalle_2(url)
            dalle = 2
        prompt = prompt.replace("-", " ")
        for punct in stopwords.punctuation:
            prompt = prompt.replace(punct, f" {punct} ")
        prompt_words = prompt.strip().split()
        urllib.request.urlretrieve(image_url, "tmp.png")
        with Image.open("tmp.png") as img:
            img.show()
        riddle = schemas.GameData(
            picture=image_url, words=prompt_words, author=author, dalle=dalle
        )
        logic = RiddleLogic(mongo_riddles=mongo, date=date)
        _approve_riddle(logic, riddle, prompt, args.force)
        date = get_date(mongo)
        url = input(f"doing {date}\nNew URL > ")
    print("done")


def _approve_riddle(logic, riddle, prompt, force):
    redacted = riddle.copy(deep=True)
    logic.redact(redacted)
    print(f"{riddle.author}'s Prompt: {prompt}")
    print(f"Redacted: {' '.join(redacted.words)}")
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
        _approve_riddle(logic, riddle, new_prompt, force)


if __name__ == "__main__":
    main()
