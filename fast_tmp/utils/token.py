# -*- encoding: utf-8 -*-
"""
@File    : token.py
@Time    : 2021/1/11 14:22
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from datetime import datetime, timedelta
from jose import jwt

from fast_tmp.conf import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(
    token: str,
):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
