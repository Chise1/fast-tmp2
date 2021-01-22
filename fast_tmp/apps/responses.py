# -*- encoding: utf-8 -*-
"""
@File    : responses.py
@Time    : 2021/1/22 16:56
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
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
