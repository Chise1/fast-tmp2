# -*- encoding: utf-8 -*-
"""
@File    : exceptions.py
@Time    : 2021/3/4 13:09
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fastapi import HTTPException
from starlette import status

credentials_exception = HTTPException(  # 登录报错
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="未登录或权限过期",
    headers={"WWW-Authenticate": "Bearer"},
)
no_permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="权限不够",
    headers={"WWW-Authenticate": "Bearer"},
)
