# -*- encoding: utf-8 -*-
"""
@File    : user.py
@Time    : 2021/1/17 17:37
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import Optional

from fastapi import Depends
from pydantic.main import BaseModel

from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.apps.api.schemas import user_list_schema, user_schema, user_create_schema
from fast_tmp.responses import Success
from fast_tmp.depends import get_superuser, PageDepend, page_depend
from fast_tmp.models import User

user_router = AmisRouter(title="用户", prefix="/user")
tpl = CRUD_TPL('用户', "get:/get", columns=get_columns_from_model(User))
tpl.add_create_button(
    "post:/post",
    get_controls_from_model(User, exclude=("id", "groups"))
)
tpl.add_modify_button(
    get_api="get:/get/?id=${id}", put_api="put:/put/${id}",
    controls=get_controls_from_model(User, exclude=("id", "groups")))
tpl.add_delete_button("delete:/delete/${id}")
user_router.registe_tpl(tpl)


class UserList(BaseModel, ):
    items: user_list_schema
    total: int


@user_router.get("/get", )
async def get_users(
    id: Optional[int] = None, user: User = Depends(get_superuser),
    page_info: PageDepend = Depends(page_depend), ):
    if id:
        x = user_schema.from_orm(await User.get(id=id))
        res = x.dict()
        res.pop("id")
        return Success(data=res)
    return Success(data={
        "total": await User.all().count(),
        "items": await user_list_schema.from_queryset(
            User.all().limit(page_info.perPage).offset(
                page_info.perPage * (page_info.page - 1)
            ).order_by('id')
        )
    })


@user_router.post("/post")
async def post_users(
    user_info: user_create_schema,
    user: User = Depends(get_superuser)
):
    u = User(**user_info.dict())
    u.set_password(user_info.password)
    await u.save()


@user_router.put("/put/${id}")
async def put_user(
    userinfo: user_create_schema, id: int,
    user: User = Depends(get_superuser)
):
    await User.filter(id=id).update(**userinfo.dict())


@user_router.delete("/delete/${id}")
async def delete_user(id: int, user: User = Depends(get_superuser)):
    await User.filter(id=id).delete()
