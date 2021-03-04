# -*- encoding: utf-8 -*-
"""
@File    : amis_html.py
@Time    : 2021/1/1 14:56
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import joinedload

from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from example.models import Message, MessageUser
from example.schemas import ResMessageList, message_schema
from fast_tmp.conf import settings
from fast_tmp.db import get_db_session

router = AmisRouter(title="信息记录", prefix="/m")
tpl = CRUD_TPL('信息记录表', 'get:/message', get_columns_from_model(Message), )
tpl.add_create_button(
    'post:/message',
    controls=get_controls_from_model(Message, exclude_pk=True), )
tpl.add_delete_button("delete:/message/${id}")
tpl.add_modify_button(
    get_api="get:/message/${id}", put_api="put:/message/${id}",
    controls=get_controls_from_model(Message, exclude_pk=True),
)
router.registe_tpl(tpl)

router.site_schema.icon = 'fa fa-file'

engine = create_async_engine(
    settings.DATABASE_URL, echo=True,
)


@router.get("/message", response_model=ResMessageList, )
async def get_message(db_session: AsyncSession = Depends(get_db_session)):
    async with db_session.begin():
        total = (await db_session.execute(func.count(Message.id))).first()[0]
        items = await db_session.execute(select(Message).join(Message.message_user))
        items = items.scalars().all()
        ist = [message_schema.from_orm(item) for item in items]
        it2 = await db_session.execute(select(Message).options(joinedload(Message.message_user)))
        print(it2.scalars().all())

        return {
            "total": total,
            "items": ist,
        }


@router.post(
    "/message",
    response_model=message_schema, codenames=['message_create']
)
async def create_message(message: message_schema):
    return await Message.create(**message.dict())


@router.put(
    "/message/${id}",
    response_model=message_schema,
)
async def put_message(id: int, message: message_schema):
    await Message.filter(id=id).update(**message.dict())
    return message


@router.get(
    "/message/${id}",
    response_model=message_schema,
)
async def get_one_message(
    id: int, db_session: AsyncSession = Depends(get_db_session)):
    async with db_session.begin():
        message = await db_session.execute(
            select(Message).where(Message.id == id).limit(1)
        )
        m1 = message.scalars().one()
        return message_schema.from_orm(m1)


@router.delete(
    "/message/${id}",
)
async def delete_message(id: int):
    await Message.filter(id=id).delete()
