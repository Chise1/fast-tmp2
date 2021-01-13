# -*- encoding: utf-8 -*-
"""
@File    : admin.py
@Time    : 2021/1/11 15:03
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import List, Union

from fastapi import Depends

from fast_tmp.amis_router import AmisRouter
from fast_tmp.conf import settings
from fast_tmp.depends import get_current_user, get_user_has_perms
from fast_tmp.models import Group, Permission, User
from fast_tmp.schemas import PermissionPageType, PermissionSchema, SiteSchema


def get_site_from_permissionschema(
    node: SiteSchema, user_codename: List[str], base_url: str, user: User
):
    if node.type == PermissionPageType.widget:
        if (
            not (node.codename and node.has_view)
            or node.codename in user_codename
            or user.is_superuser
        ):
            # fixme:临时措施
            if node.url == "/schema_api":
                return False
            return True
        else:
            return False
    else:
        if node.children:
            res = [
                get_site_from_permissionschema(child_node, user_codename, base_url + node.url, user)
                for child_node in node.children
            ]
            if any(res):
                if node.type == PermissionPageType.page:
                    return {
                        "label": node.label,
                        "type": "page",
                        "icon": node.icon,
                        "url": base_url + node.url,
                        "schemaApi": base_url + node.url + node.schema_api,
                        "rewrite": node.rewrite,
                        "visable": node.visable,
                        "redirect": node.redirect,
                    }
                else:
                    if any(
                        [
                            child_node.type == PermissionPageType.widget
                            for child_node in node.children
                        ]
                    ):
                        return {
                            "type": "page",
                            "label": node.label,
                            "icon": node.icon,
                            "url": base_url + node.url,
                            "children": [i for i in res if i],
                        }
                    else:
                        return {
                            "type": "route",
                            "label": node.label,
                            "icon": node.icon,
                            "children": [i for i in res if i],
                        }
            else:
                return None
        else:
            return None


async def init_permission(node: Union[SiteSchema, PermissionSchema], permissions: List[Permission]):
    if node.codename:
        for permission in permissions:
            if permission.codename == node.codename:
                break
        else:
            p = await Permission.create(codename=node.codename, label=node.label)
            permissions.append(p)
    if node.children:
        for child_node in node.children:
            await init_permission(child_node, permissions)


admin_app = AmisRouter(prefix="/admin")


@admin_app.post("/user", summary="summary", description="desc")
async def create_user(username: str, password: str):
    user = User(username=username)
    user.set_password(password)
    await user.save()
    return


INIT_PERMISSION = False


@admin_app.get("/site")
async def get_site(user: User = Depends(get_current_user)):
    """
    获取token
    :param user:
    :return:
    """
    global INIT_PERMISSION
    from example.main import app

    # 初始化permission
    if not INIT_PERMISSION:
        await init_permission(app.site_schema, list(await Permission.all()))
        INIT_PERMISSION = True
    permissions = await user.perms
    site = get_site_from_permissionschema(app.site_schema, permissions, settings.SERVER_URL, user)
    return site


@admin_app.post("/permission")
async def create_permission(label: str, codename: str):
    p = await Permission.create(label=label, codename=codename)
    return p


@admin_app.post("/group")
async def create_group(
    label: str,
    users: List[int],
    permissions: List[int],
    user: User = Depends(get_user_has_perms(["t1"])),
):
    g = await Group.create(label=label)
    x = await Permission.filter(id__in=permissions)
    users = await User.filter(id__in=users)
    for user in users:
        await user.groups.add(g)
    await g.permissions.add(*x)
