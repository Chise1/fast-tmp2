from typing import Optional

from fastapi import Depends
from tortoise.transactions import in_transaction

from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.apps.api.schemas import GroupS, group_list_schema
from fast_tmp.depends import PageDepend, get_user_has_perms, page_depend
from fast_tmp.models import Group, Permission, User
from fast_tmp.responses import Success

group_router = AmisRouter(title="用户组", prefix="/u")

tpl = CRUD_TPL("用户组", "get:/group", columns=get_columns_from_model(Group))
tpl.add_create_button("post:/group", get_controls_from_model(Group, exclude=("id",)))
tpl.add_modify_button(
    get_api="get:/group/?id=${id}",
    put_api="put:/group/${id}",
    controls=get_controls_from_model(Group, exclude=("id",)),
)
tpl.add_delete_button("delete:/group/${id}")
group_router.registe_tpl(tpl)


@group_router.get("/group")
async def get_group(
    id: Optional[int] = None,
    page_info: PageDepend = Depends(page_depend),
    user: User = Depends(get_user_has_perms(["group_can_read"])),
):
    if id:
        x: Group = await Group.get(id=id).prefetch_related("permissions", "users")
        return Success(
            data=GroupS(
                label=x.label,
                permissions=[i.id for i in x.permissions],
                users=[i.pk for i in x.users],
            ).dict()
        )
    return Success(
        data={
            "total": await Group.all().count(),
            "items": await group_list_schema.from_queryset(
                Group.all()
                .limit(page_info.perPage)
                .offset(page_info.perPage * (page_info.page - 1))
                .order_by("id")
            ),
        }
    )


@group_router.post("/group")
async def post_group(
    group: GroupS,  # fixme:无法直接获取多对多字段
    user: User = Depends(get_user_has_perms(["group_can_read"])),
):
    cr_g = await Group.create(label=group.label)
    permissions = await Permission.filter(id__in=group.permissions)
    users = await User.filter(id__in=group.users)
    # fixme:tortoise-orm的多对多字段很难用，需要访问多次数据库，以后考虑更换为sqlalchemy
    await cr_g.permissions.add(*permissions)
    await cr_g.users.add(*users)


@group_router.put("/group/${id}")
async def put_group(
    group: GroupS,
    id: int,
    user: User = Depends(get_user_has_perms(["group_can_read"])),
):
    g = await Group.get(id=id)
    async with in_transaction() as connection:
        await g.users.clear()
        await g.permissions.clear()
        if group.users:
            await g.users.add(*await User.filter(id__in=group.users))
        if group.permissions:
            await g.permissions.add(*await Permission.filter(id__in=group.permissions))


@group_router.delete("/group/${id}")
async def put_group(
    id: int,
    user: User = Depends(get_user_has_perms(["group_can_read"])),
):
    g = await Group.get(id=id)
    await g.delete()


@group_router.get("/permissions-selects")
async def get_permission_select():
    x = await Permission.all()
    res = [{"label": permission.label, "value": permission.pk} for permission in x]
    return Success(data=res)


@group_router.get("/users-selects")
async def get_users_select():
    x = await User.all()
    res = [{"label": user.username, "value": user.pk} for user in x]
    return Success(data=res)
