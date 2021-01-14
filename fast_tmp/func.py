from typing import List, Union

from fast_tmp.models import Group, Permission, User
from fast_tmp.schemas import PermissionPageType, PermissionSchema, SiteSchema


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
