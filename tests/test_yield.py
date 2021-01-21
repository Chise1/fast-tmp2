# -*- encoding: utf-8 -*-
"""
@File    : test_yield.py
@Time    : 2021/1/21 11:09
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import Generator
import pytest
def stop():
    print("执行stop")


def client():
    print("执行client")

@pytest.fixture(scope='session',autouse=True)
def start() -> Generator:
    print("start")
    yield client
    stop()

@pytest.mark.asyncio
async def test_yield():
    print("执行yield")

@pytest.mark.asyncio
async def test_yield2():
    print("执行yield2")