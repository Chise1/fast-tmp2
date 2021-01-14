from fastapi import Depends
from pydantic.main import BaseModel
from tortoise.contrib.pydantic import pydantic_queryset_creator

from fast_tmp.amis.schema.actions import DrawerAction
from fast_tmp.amis.schema.buttons import Operation
from fast_tmp.amis.schema.crud import CRUD
from fast_tmp.amis.schema.forms import Form
from fast_tmp.amis.schema.frame import Drawer
from fast_tmp.amis.utils import get_coulmns_from_pqc
from fast_tmp.amis_router import AmisRouter
from fast_tmp.depends import get_superuser
from fast_tmp.models import Permission, User

permission_router = AmisRouter(title="权限", prefix="/permission")
permission_list_schema = pydantic_queryset_creator(Permission)


class PermissionList(BaseModel):
    items: permission_list_schema
    total: int


@permission_router.get(
    "/permission",
    view=CRUD(
        columns=get_coulmns_from_pqc(
            permission_list_schema,
            add_type=False,  # extra_fields=[
            #     Operation(
            #         label="修改",
            #         buttons=[
            #             DrawerAction(
            #                 label="修改",
            #                 drawer=Drawer(
            #                     title="修改数据",
            #                     body=Form(
            #                         name="message_update",
            #                         api="put:"
            #                             + settings.SERVER_URL
            #                             + router.prefix
            #                             + "/message/${id}",
            #                         initApi=settings.SERVER_URL + router.prefix + "/message/${id}",
            #                         controls=get_columns_from_model(Message, add_type=True),  # 测试这里
            #                     ),
            #                 ),
            #             ),
            #             AjaxAction(
            #                 label="删除",
            #                 level=ButtonLevelEnum.danger,
            #                 confirmText="确认要删除？",
            #                 api="delete:http://127.0.0.1:8000/amis/message/${id}",
            #             ),
            #         ],
            #     )
            # ],
        ),
    ),
    response_model=PermissionList,
)
async def get_permissions(user: User = Depends(get_superuser)):
    return {"items": await Permission.all(), "total": await Permission.all().count()}
