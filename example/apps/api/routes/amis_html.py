# -*- encoding: utf-8 -*-
"""
@File    : amis_html.py
@Time    : 2021/1/1 14:56
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from example.models import Message
from example.schemas import ResMessageList, message_list_schema, message_schema

router = AmisRouter(title="信息记录",prefix="/m")
tpl = CRUD_TPL('信息记录表', 'get:/message', get_columns_from_model(Message), )
tpl.add_create_button('post:/message',
                      get_controls_from_model(Message, exclude_readonly=True), )
tpl.add_delete_button("delete:/message/${id}")
tpl.add_modify_button(
    get_api="get:/message/${id}", put_api="put:/message/${id}",
    controls=get_controls_from_model(Message, exclude_readonly=True),
)
router.registe_tpl(tpl)

router.site_schema.icon = 'fa fa-file'


@router.get("/message", response_model=ResMessageList, )
async def get_message():
    return {
        "total": await Message.all().count(),
        "items": await message_list_schema.from_queryset(Message.all()),
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
async def get_one_message(id: int):
    return await Message.get(id=id)


@router.delete(
    "/message/${id}",
)
async def delete_message(id: int):
    await Message.filter(id=id).delete()
# fixme:修改路由规则，所有路由里面不要加$符号，将有特殊意义
