from collections import Iterable
from typing import List, Union

from fast_tmp.models import Permission, User
from fast_tmp.schemas import PermissionPageType, PermissionSchema, SiteSchema


def has_perm(user_codename: List[str], codenames: List[str]):
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
    page = node.page
    res = None
    if node.children:
        for widget in node.children:
            if widget.codename:
                if not (user.is_superuser or has_perm(user_codename, widget.codename)):
                    continue
            if widget.view:
                if hasattr(widget.view, "api"):
                    d = widget.view.dict()
                    d["api"] = url + widget.view.api
                    # widget.view.api = url + widget.view.api
                res = page.dict()
                res["body"].append(d)
    if res and res["body"]:
        return res
    return None


def get_site_from_permissionschema(
    node: SiteSchema, user_codename: List[str], base_url: str, user: User
):
    if node.type == PermissionPageType.widget:
        if (
            (not node.codename and node.has_view)
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
                        "schema": get_schema_from_page(
                            node,
                            user_codename,
                            base_url,
                            user,
                        ),
                        # "schemaApi": base_url + node.url + node.schema_api,
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


def get_site_from_permissionschema_v2(
    node: SiteSchema, user_codename: List[str], base_url: str, user: User
):
    if node.type == PermissionPageType.route:
        res = {
            "label": node.label,
            "icon": node.icon,
            "children": [],
        }
        if not node.children:
            return None
        for child_node in node.children:
            x = get_site_from_permissionschema_v2(
                child_node, user_codename, base_url + node.url, user
            )
            if x:
                res["children"].append(x)
        if not res["children"]:
            return None
        return res
    elif node.type == PermissionPageType.page:
        url = base_url + node.url
        schema = get_schema_from_page(node, user_codename, url, user)
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
                x = get_site_from_permissionschema_v2(
                    child_node, user_codename, base_url + node.url, user
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
