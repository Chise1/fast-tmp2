# -*- encoding: utf-8 -*-
"""
@File    : amis_html.py
@Time    : 2021/1/1 14:56
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import Optional

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, joinedload

from example.models import Message, MessageUser
from example.schemas import ResMessageList, message_schema, user_schema
from fast_tmp.amis.creator import create_list_route
from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.conf import settings
from fast_tmp.db import get_db_session
from fast_tmp.models import User

router = AmisRouter(title="信息记录", prefix="/m")
tpl = CRUD_TPL(
    "信息记录表",
    "get:/message",
    get_columns_from_model(Message),
)
tpl.add_create_button(
    "post:/message",
    controls=get_controls_from_model(Message, exclude_pk=True),
)
tpl.add_delete_button("delete:/message/${id}")
tpl.add_modify_button(
    get_api="get:/message/${id}",
    put_api="put:/message/${id}",
    controls=get_controls_from_model(Message, exclude_pk=True),
)
router.registe_tpl(tpl)

router.site_schema.icon = "fa fa-file"


@router.get(
    "/message",
    response_model=ResMessageList,
)
def get_message(page: int = 0, perPage: int = 10, db_session: Session = Depends(get_db_session)):
    total = db_session.execute(func.count(Message.id)).first()[0]
    items = (
        db_session.execute(
            select(Message).join(Message.message_user).limit(perPage).offset(perPage * (page - 1))
        )
        .scalars()
        .all()
    )
    ist = [message_schema.from_orm(item) for item in items]
    # it2 = db_session.execute(select(Message).options(joinedload(Message.message_user)))
    return {
        "total": total,
        "items": ist,
    }


create_list_route(
    router, "/message1", Message, message_schema, [], filters=["id"], searchs=["info"]
)
create_list_route(
    router,
    "/user",
    User,
    user_schema,
    [],
)


@router.post("/message", response_model=message_schema, codenames=["message_create"])
def create_message(message: message_schema, session: Session = Depends(get_db_session)):
    data = message.dict()
    print(data)
    ret = Message(**data)
    session.add(ret)
    session.commit()
    return ret


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
async def get_one_message(id: int, db_session: AsyncSession = Depends(get_db_session)):
    async with db_session.begin():
        message = await db_session.execute(select(Message).where(Message.id == id).limit(1))
        m1 = message.scalars().one()
        return message_schema.from_orm(m1)


@router.delete(
    "/message/${id}",
)
async def delete_message(id: int):
    await Message.filter(id=id).delete()
