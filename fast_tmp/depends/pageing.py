# -*- encoding: utf-8 -*-
"""
@File    : pageing.py
@Time    : 2021/1/18 10:11
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :分页
"""
from pydantic.main import BaseModel


class PageDepend(BaseModel):  # 分页
    perPage: int = 10
    page: int = 1


def page_depend(perPage: int = 10, page: int = 1) -> PageDepend:
    return PageDepend(page=page, perPage=perPage)
