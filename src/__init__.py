# -*- encoding: utf-8 -*-
"""
@File    : __init__.py
@Time    : 2021/1/8 22:10
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from rearq import ReArq

from src import settings

rearq = ReArq(**settings.REARQ,)
