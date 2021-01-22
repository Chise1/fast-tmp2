# -*- encoding: utf-8 -*-
"""
@File    : error_code.py
@Time    : 2021/1/22 16:46
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from pydantic.main import BaseModel


class BaseError(BaseModel):
    error: int
    msg: str


class LoginError(BaseError):
    status = 1
    msg: str = "账户或密码错误"
