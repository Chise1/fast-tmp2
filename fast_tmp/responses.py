from typing import Any, Dict, List

from pydantic import BaseModel


class Success(BaseModel):
    status: int = 0
    msg: str = ""
    data: Any = None


class TokenOut(Success):
    class TokenDataModel(BaseModel):
        access_token: str
        token_type: str = "bearer"

    data: TokenDataModel

class BaseError(BaseModel):
    error: int
    msg: str

class LoginError(BaseError):
    status = 1
    msg: str = "账户或密码错误"
