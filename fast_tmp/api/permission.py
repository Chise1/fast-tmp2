from typing import Optional

from fastapi import Depends
from pydantic.main import BaseModel

from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.api.schemas import permission_list_schema, permission_schema, permission_create_schema
from fast_tmp.depends import get_superuser
from fast_tmp.models import Permission, User

permission_router = AmisRouter(title="权限", prefix="/p")
tpl = CRUD_TPL('权限', "get:/permission", columns=get_columns_from_model(Permission))
tpl.add_create_button("post:/permission",
                      get_controls_from_model(Permission, exclude=("id", "groups"))
                      )
tpl.add_modify_button(
    get_api="get:/permission/?id=${id}", put_api="put:/permission/${id}",
    controls=get_controls_from_model(Permission, exclude=("id", "groups")))
tpl.add_delete_button("delete:/permission/${id}")
permission_router.registe_tpl(tpl)


class PermissionList(BaseModel, ):
    items: permission_list_schema
    total: int


@permission_router.get("/permission", )
async def get_permissions(id: Optional[int] = None, user: User = Depends(get_superuser)):
    if id:
        x = permission_schema.from_orm(await Permission.get(id=id))
        res = x.dict()
        res.pop("id")
        return res
    return {
        "total": await Permission.all().count(),
        "items": await permission_list_schema.from_queryset(Permission.all())
    }


@permission_router.post("/permission")
async def post_permissions(
    permission_schema: permission_create_schema,
    user: User = Depends(get_superuser)
):
    await Permission.create(**permission_schema.dict())


@permission_router.put("/permission/${id}")
async def put_permission(
    permission_schema: permission_create_schema, id: int,
    user: User = Depends(get_superuser)):
    await Permission.filter(id=id).update(**permission_schema.dict())


@permission_router.delete("/permission/${id}")
async def delete_permission(id: int, user: User = Depends(get_superuser)):
    p = await Permission.filter(id=id).delete()
