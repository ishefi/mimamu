#!/usr/bin/env python
import random
import time

from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from common import config


def verify_token(
    x_mmm_token: str | None = Header(default=None), mmm_token: str | None = None
) -> None:
    if not _verify(x_mmm_token) and not _verify(mmm_token):
        time.sleep(random.random() * 2)
        raise HTTPException(status.HTTP_403_FORBIDDEN)


def _verify(mmm_token: str | None) -> bool:
    if mmm_token is None:
        return False
    elif mmm_token != config.SECRET_TOKEN:
        return False
    else:
        return True
