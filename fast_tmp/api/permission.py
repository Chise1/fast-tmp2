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

permission_router = AmisRouter(title="权限")
permission_list_schema = pydantic_queryset_creator(Permission, exclude=("groups",))


class PermissionList(
    BaseModel,
):
    items: permission_list_schema
    total: int


@permission_router.get(    "/permission",       response_model=PermissionList,
)
async def get_permissions(user: User = Depends(get_superuser)):
    return {"items": await Permission.all(), "total": await Permission.all().count()}
