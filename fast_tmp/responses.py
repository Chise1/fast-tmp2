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
