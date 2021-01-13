# -*- encoding: utf-8 -*-
"""
@File    : amis_html.py
@Time    : 2021/1/1 14:56
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fast_tmp.amis.schema.actions import AjaxAction, DialogAction, DrawerAction
from fast_tmp.amis.schema.buttons import Operation
from fast_tmp.amis.schema.crud import CRUD
from fast_tmp.amis.schema.enums import ButtonLevelEnum
from fast_tmp.amis.schema.forms import Form
from fast_tmp.amis.schema.frame import Dialog, Drawer
from fast_tmp.amis.utils import get_coulmns_from_pmc, get_coulmns_from_pqc, get_columns_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.conf import settings
from example.models import Message
from example.schemas import ResMessageList, message_list_schema, message_schema

router = AmisRouter(prefix="/amis")


@router.get(
    "/message",
    view=CRUD(
        api=settings.SERVER_URL + router.prefix + "/message",
        columns=get_coulmns_from_pqc(
            message_list_schema,
            add_type=False,
            extra_fields=[
                Operation(
                    label="修改",
                    buttons=[
                        DrawerAction(
                            label="修改",
                            drawer=Drawer(
                                title="修改数据",
                                body=Form(
                                    name="message_update",
                                    api="put:"
                                        + settings.SERVER_URL
                                        + router.prefix
                                        + "/message/${id}",
                                    initApi=settings.SERVER_URL + router.prefix + "/message/${id}",
                                    controls=get_columns_from_model(Message, add_type=True),  # 测试这里
                                ),
                            ),
                        ),
                        AjaxAction(
                            label="删除",
                            level=ButtonLevelEnum.danger,
                            confirmText="确认要删除？",
                            api="delete:http://127.0.0.1:8000/amis/message/${id}",
                        ),
                    ],
                )
            ],
        ),
    ),
    response_model=ResMessageList,
)
async def get_message():
    return {
        "total": await Message.all().count(),
        "items": await message_list_schema.from_queryset(Message.all()),
    }


@router.post(
    "/message",
    view=DialogAction(
        label="新增",
        dialog=Dialog(
            title="新增",
            body=Form(
                name="message_create",
                controls=get_columns_from_model(Message, add_type=True),
                api="http://127.0.0.1:8000/amis/message",
            ),
        ),
    ),
    response_model=message_schema,
)
async def create_message(message: message_schema):
    return await Message.create(**message.dict())


@router.put(
    "/message/{id}",
    response_model=message_schema,
)
async def put_message(id: int, message: message_schema):
    await Message.filter(id=id).update(**message.dict())
    return message


@router.get(
    "/message/{id}",
    response_model=message_schema,
)
async def get_one_message(id: int):
    return await Message.get(id=id)


@router.delete(
    "/message/{id}",
)
async def delete_message(id: int):
    await Message.filter(id=id).delete()
