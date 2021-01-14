# -*- encoding: utf-8 -*-
"""
@File    : t.py
@Time    : 2021/1/14 12:34
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from pydantic import BaseModel


class M:
    p = ""

    def __init__(self, p):
        self.p = p


class A(BaseModel):
    x: M = M("dd")


a = A()

print(a.dict())
