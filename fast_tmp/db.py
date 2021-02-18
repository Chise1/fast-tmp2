# -*- encoding: utf-8 -*-
"""
@File    : db.py
@Time    : 2021/2/17 9:56
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fast_tmp.conf import settings

SessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=create_async_engine(settings.ASYNC_ENGINE, echo=True),
)


async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
