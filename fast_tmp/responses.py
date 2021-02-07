from typing import Any, Dict, List

from fastapi import HTTPException


class BaseError(HTTPException):
    error: int
    msg: str


class LoginError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail={"code": 1, "msg": "账户或密码错误", "detail": ""},
            headers={"WWW-Authenticate": "Bearer"},
        )
