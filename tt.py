# -*- encoding: utf-8 -*-
"""
@File    : tt.py
@Time    : 2021/1/15 8:58
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""


class Api(str):
    base_url = ""

    def __str__(self):
        return self.base_url + super().__str__()
a1=Api("ddd")
a2=Api("xxx")
l=[a1,a2]
l[0].base_url="xxxxsefefqe"
print(a1)