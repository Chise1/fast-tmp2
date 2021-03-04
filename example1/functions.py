# -*- encoding: utf-8 -*-
"""
@File    : functions.py
@Time    : 2021/2/18 14:39
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_tmp.conf import settings
from fast_tmp.models import User

engine = create_async_engine(settings.ASYNC_ENGINE)


async def get_userinfo(username: str):
    """
    把单点登录得到的用户名转为当前的用户
    同时检查如果在数据库没有该函数则报错
    """
    async with AsyncSession(engine) as session:
        async with session.begin():
            results = await session.execute(select(User).where(username == username))
            user = results.scalars().first()
            if not user:
                user = User(username=username)
                session.add(user)
                await session.flush()
    return user
