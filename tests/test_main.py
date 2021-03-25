# -*- encoding: utf-8 -*-
"""
@File    : test_main.py
@Time    : 2021/3/12 17:11
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from starlette.testclient import TestClient

from example.main import app
client=TestClient(app)
