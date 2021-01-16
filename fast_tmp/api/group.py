from fastapi import Depends
from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis_router import AmisRouter
from fast_tmp.api.schemas import GroupGetList, group_list_schema, group_schema, GroupS
from fast_tmp.models import User, Group, Permission
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.depends import get_user_has_perms

group_router = AmisRouter(title="用户组")

tpl = CRUD_TPL('用户组', "get:/group", columns=get_columns_from_model(Group))
tpl.add_create_button("post:/group", get_controls_from_model(Group, exclude=("id",)))
group_router.registe_tpl(tpl)


@group_router.get("/group", response_model=GroupGetList)
async def get_group(user: User = Depends(get_user_has_perms(['group_can_read']))):
    return {
        "total": await Group.all().count(),
        "items": await group_list_schema.from_queryset(Group.all().order_by("id", )),
    }


@group_router.post("/group")
async def post_group(group: GroupS,  # fixme:无法直接获取多对多字段
                     user: User = Depends(get_user_has_perms(['group_can_read'])), ):
    cr_g = await Group.create(label=group.label)
    permissions = await Permission.filter(id__in=group.permissions.split(","))
    users=await User.filter(id__in=group.users.split(","))
    # fixme:tortoise-orm的多对多字段很难用，需要访问多次数据库，以后考虑更换为sqlalchemy
    await cr_g.permissions.add(*permissions)
    await cr_g.users.add(*users)


@group_router.get("/permissions-selects")
async def get_permission_select():
    x = await Permission.all()
    res = [{"label": permission.label, "value": permission.pk} for permission in x]
    return res


@group_router.get("/users-selects")
async def get_users_select():
    x = await User.all()
    res = [{"label": user.username, "value": user.pk} for user in x]
    return res
