# -*- encoding: utf-8 -*-
"""
@File    : exceptions.py
@Time    : 2021/3/12 9:21
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fastapi import Request
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status


async def error_exception_handler(request: Request, exc: IntegrityError):
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail)
