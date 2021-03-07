# -*- encoding: utf-8 -*-
"""
@File    : test_inspect.py
@Time    : 2021/3/7 8:38
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import inspect
from typing import List


def a(x: int, y: int, **kwargs):
    pass


def add_filter(func, filters: List[str]):
    signature = inspect.signature(func)
    res = []
    # signature=inspect.Signature()
    for k, v in signature.parameters.items():
        if k == "kwargs":
            continue
        res.append(v)
    for filter_ in filters:
        res.append(
            inspect.Parameter(filter_, kind=inspect.Parameter.KEYWORD_ONLY, annotation=str)
        )  # fixme:之后支持根据字段类型进行自定义
    func.__signature__ = inspect.Signature(parameters=res, __validate_parameters__=False)


add_filter(a, ["chise"])
print(inspect.signature(a))
