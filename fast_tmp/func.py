from collections import Iterable
from typing import List, Union

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


# fixme:增加缓存
def get_schema_from_page(
    node: SiteSchema,
    user_codename: List[str],
    url,
    user: User,
):
    res = node.get_view_dict(user_codename, user.is_superuser, url)
    return res


def get_site_from_permissionschema(
    node: SiteSchema, user_codename: List[str], base_url: str, is_superuser:bool
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
                    res['children']=[x]
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
            # "rewrite":url,
            # "redirect":base_url + node.url,
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


async def create_perm(codename, label, permissions):
    for permission in permissions:
        if permission.codename == codename:
            return
    else:
        p = await Permission.get_or_create(codename=codename, defaults={"label": label})
        permissions.append(p)


async def init_permission(node: Union[SiteSchema, PermissionSchema], permissions: List[Permission]):
    if node.codename:
        if not isinstance(node.codename, Iterable):
            await create_perm(node.codename, node.label, permissions)
        else:
            for codename in node.codename:
                await create_perm(codename, codename, permissions)
    if getattr(node, "children", None):
        for child_node in node.children:
            await init_permission(child_node, permissions)
