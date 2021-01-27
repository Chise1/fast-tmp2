# -*- encoding: utf-8 -*-
"""
@File    : test_fastapi_asyncio.py
@Time    : 2021/1/21 12:35
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import pytest
from httpx import AsyncClient

from src.main import app

from fast_tmp.models import User


@pytest.mark.asyncio  # 所有异步都不能少
async def test_root():
    await User.all().count()  # 愉快的调用tortoise-orm的model进行数据操作
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/fast/auth/index")
    assert response.status_code == 200
