# -*- encoding: utf-8 -*-
"""
@File    : test_asyncio.py
@Time    : 2021/1/21 11:37
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import pytest

from fast_tmp.models import User


@pytest.mark.asyncio
async def test_user():
    print("test user")
    assert await User.all().count() == 0


@pytest.mark.asyncio
async def test_user2():
    assert await User.create(username='test', password='mininet')
