#!/usr/bin/env python
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi import status


def verify_token(request: Request, x_mmm_token: str | None = Header(default=None)):
    if x_mmm_token is None or x_mmm_token != request.app.state.secret_token:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
