# -*- encoding: utf-8 -*-
"""
@File    : test_metaclass.py
@Time    : 2020/12/16 0:05
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""


# 测试继承的
class PaginatorDepends(object):
    def __init__(self, queryset: str):
        print("我被初始化了:", str(queryset))

    pass


class MediaMetaClass(type):
    """
    处理一部分信息
    """

    def __new__(cls, name, bases, attrs):
        attrs["__name__"] = name
        new_class = type.__new__(cls, name, bases, attrs)
        if attrs.get("paginator"):
            list_queryset = attrs.get("get_queryset")(new_class)
            attrs["paginator"] = attrs.get("paginator")(list_queryset)
        return new_class


class Admin(metaclass=MediaMetaClass):
    paginator = PaginatorDepends
    model: str

    def __init__(self):
        print("init")

    def get_queryset(self):
        return "queryset"

