# -*- encoding: utf-8 -*-
"""
@File    : t.py
@Time    : 2021/2/9 8:55
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import List
from fastapi import Depends
from pydantic.main import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from example.schemas import user_schema, permission_schema
from fast_tmp.amis_router import AmisRouter
from fast_tmp.conf import settings
from fast_tmp.db import get_db_session
from fast_tmp.models import User, Permission, Group, group_user, \
    group_permission

engine = create_async_engine(settings.ASYNC_ENGINE)
t_route = AmisRouter(title="测试", prefix="/test")


@t_route.get("/users")
async def get_users(username: str,
                    session: AsyncSession = Depends(get_db_session)):
    async with session.begin():
        result = await session.execute(
            select(User).where(
                username == username
            )
        )
        f = result.scalars().first()
        f.set_password("mininet")
        await session.flush()
        return user_schema.from_orm(f)


@t_route.put("/user/password")
async def get_users(username: str, password,
                    session: AsyncSession = Depends(get_db_session)):
    async with session.begin():
        result = await session.execute(
            select(User).where(
                username == username
            )
        )
        f = result.scalars().first()
        f.set_password(password)
        await session.flush()
        return user_schema.from_orm(f)


@t_route.post("/user")
async def create_user(
    username: str, password: str, session=Depends(get_db_session)):
    """
    创建用户
    """
    user = User(
        # id=1,
        username=username,
        password=password
    )
    async with session.begin():
        session.add(user)
        await session.flush()
    return user


@t_route.post("/group")
async def create_group(name: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            # group = Group(name=name)
            # session.add(group)
            # await session.flush()
            await session.execute(
                Group.metadata.tables[Group.__tablename__], [{"name": name}]
            )
    return True


@t_route.get("/group")
async def get_group_list(db_session: AsyncSession = Depends(get_db_session)):
    async with db_session.begin():
        results = await db_session.execute(
            select(Group)
        )
        res = results.scalars().fetchall()
        return [{"id": group.id, "name": group.name} for group in res]


class CreateGroupUserPerm(BaseModel):
    users: List[int]
    perms: List[str]
    group_id: int


@t_route.post("/group/users")
async def create_group_users(
    cgp: CreateGroupUserPerm,
    session: AsyncSession = Depends(
        get_db_session
    )
):
    # 方法一
    # def p(session):
    #     group: Group = session.execute(
    #         select(Group).where(Group.id == cgp.group_id).limit(
    #             1)).scalars().first()
    #     permissions=session.execute(
    #         select(Permission).where(Permission.code.in_(cgp.perms))
    #     ).scalars().fetchall()
    #     for perm in permissions:
    #         group.permissions.append(perm)
    #
    #     users = session.execute(
    #         select(User).where(User.id.in_(cgp.users))
    #     ).scalars().fetchall()
    #     for user in users:
    #         group.users.append(user)
    # async with session.begin():
    #     await session.run_sync(p)
    # 方法二
    async with session.begin():
        await session.execute(
            group_user.insert(),
            [
                {"group_id": cgp.group_id, "user_id": user_id} for user_id in
                cgp.users
            ]
        )
        await session.execute(
            group_permission.insert(),
            [
                {
                    "group_id": cgp.group_id,
                    "permission_code": perm
                } for perm in cgp.perms
            ]
        )
        # group: Group = (await session.execute(
        #     select(Group).where(Group.id == cgp.group_id).limit(1))).scalars().first()
        # for perm in cgp.perms:
        #     group.permissions.append(perm)
        # for user_id in cgp.users:
        #     group.users.append(user_id)
        await session.flush()


@t_route.get("/permissions")
async def get_permission_list(session: AsyncSession = Depends(get_db_session)):
    async with session.begin():
        permissions = (await session.execute(
            select(Permission)
        )).scalars().fetchall()
        return [permission_schema.from_orm(permission) for permission in
                permissions]


@t_route.post("/permission")
async def create_permission(
    perm: permission_schema,
    session: AsyncSession = Depends(get_db_session)
):
    async with session.begin():
        permission = Permission(**perm.dict())
        session.add(permission)
        await session.flush()
