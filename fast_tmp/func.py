from typing import Iterable, List, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_tmp.conf import settings
from fast_tmp.models import Permission, User
from fast_tmp.schemas import PermissionPageType, PermissionSchema, SiteSchema


def check_perms(user_codename: List[str], codenames: List[str]):
    for c in codenames:
        for u_c in user_codename:
            if c == u_c:
                break
        else:
            return False
    return True


# fixme:增加缓存d
def get_schema_from_page(
    node: SiteSchema,
    user_codename: List[str],
    url,
    user: User,
):
    res = node.get_view_dict(user_codename, user.is_superuser, url)
    return res


def get_site_from_permissionschema(
    node: SiteSchema, user_codename: List[str], base_url: str, is_superuser: bool
):
    if node.type == PermissionPageType.route:
        res = {
            "label": node.label,
            "icon": node.icon,
        }
        if not node.children:
            return None
        for child_node in node.children:
            x = get_site_from_permissionschema(
                child_node, user_codename, base_url + node.url, is_superuser
            )
            if x:
                if res.get("children"):
                    res["children"].append(x)
                else:
                    res["children"] = [x]
        if not res.get("children"):
            return None
        return res
    elif node.type == PermissionPageType.page:
        url = base_url + node.url
        schema = node.get_view_dict(user_codename, is_superuser, base_url)
        if not schema:
            return None
        res = {
            "label": node.label,
            "icon": node.icon,
            "url": url,
            "schema": schema,
            "rewrite": url,
            "redirect": url,
        }
        if node.children:
            for child_node in node.children:
                x = get_site_from_permissionschema(
                    child_node, user_codename, base_url + node.url, is_superuser
                )
                if x:
                    if res.get("children"):
                        res["children"].append(x)
                    else:
                        res["children"] = []
                        res["children"].append(x)
        return res
    else:
        return None


def create_perm(codename, label, permissions: List[str], session: Session):
    for permission in permissions:
        if permission == codename:
            return
    else:
        # fixme:增加一个报错拦截
        p = Permission(code=codename, name=label)
        session.add(p)
        session.commit()
        permissions.append(p.code)


def init_permission(
    node: Union[SiteSchema, PermissionSchema], permissions: List[str], session: Session
):
    if node.codename:
        if not isinstance(node.codename, Iterable):
            create_perm(node.codename, node.label, permissions, session)
        else:
            for codename in node.codename:
                create_perm(codename, codename, permissions, session)
    if getattr(node, "children", None):
        for child_node in node.children:
            init_permission(child_node, permissions, session)


def get_userinfo(username: str, session: Session):
    """
    把单点登录得到的用户名转为当前的用户
    同时检查如果在数据库没有该函数则报错
    """
    results = session.execute(select(User).where(username == username))
    user = results.scalars().first()
    if not user:
        user = User(username=username)
        session.add(user)
        session.commit()
    return user
