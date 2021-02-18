# -*- encoding: utf-8 -*-
"""
@File    : t.py
@Time    : 2021/2/9 8:55
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fast_tmp.amis_router import AmisRouter
from fast_tmp.conf import settings
from fast_tmp.depends.cas import cas_get_user
from fast_tmp.models import Base, User, Permission, Group

engine = create_async_engine(settings.ASYNC_ENGINE)
t_route = AmisRouter(title="测试", prefix="/test")


@t_route.get("/users")
async def get_users(user=Depends(cas_get_user)):
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
    print(user)
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(
                select(User)
            )
            f = result.scalars().first()
            if not f:
                return
            f.password = "zhangsan"
            await session.flush()
    return f


@t_route.post("/user")
async def create_user(username: str, password: str):
    """
    创建用户
    """
    user = User(
        # id=1,
        username=username,
        password=password
    )
    async with AsyncSession(engine) as session:
        async with session.begin():
            session.add(user)
            await session.flush()
    return user


@t_route.post("/permission")
async def create_permission(code: str, name: str):
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        async with session.begin():
            permission = Permission(code=code, name=name)
            await session.add(permission)
    return True


@t_route.post("/group")
async def create_group(name: str):
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        async with session.begin():
            permission = Group(name=name)
            session.add(permission)
            await session.flush()
    return True
