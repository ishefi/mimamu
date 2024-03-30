#!/usr/bin/env python
import random
import time

from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from common import config


def verify_token(x_mmm_token: str | None = Header(default=None)) -> None:
    if x_mmm_token is None or x_mmm_token != config.SECRET_TOKEN:
        time.sleep(random.random() * 2)
        raise HTTPException(status.HTTP_403_FORBIDDEN)
