# -*- encoding: utf-8 -*-
"""
@File    : schemas.py
@Time    : 2021/1/11 16:48
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic.main import BaseModel

from fast_tmp.amis.tpl import TPL


class PermissionPageType(str, Enum):
    page = "page"
    route = "route"


class PermissionSchema(BaseModel):
    label: str
    codename: List[str] = []
    type: PermissionPageType = PermissionPageType.page
    url: str = ""  # 基础路由，用户请勿初始化


class SiteSchema(PermissionSchema):
    icon: Optional[str]
    link: Optional[str]
    redirect: Optional[str]
    rewrite: bool = False
    visable: bool = True
    children: List["SiteSchema"] = []  # 子页面
    amis_tpl: Optional[Any]
    request_codename: Dict[
        str, List[Dict[str, List[str]]]
    ] = {}  # 记录接口所需的权限,path:[{methods:[],codenames:[]}]

    def registe_view(self, tpl: TPL):
        self.amis_tpl = tpl

    def get_view_dict(self, codenames: List[str], is_superuser: bool, server_url):
        """
        获取view信息
        """
        if not self.amis_tpl:
            return None
        res = self.amis_tpl.get_view_dict(
            codenames, is_superuser, server_url + self.url, self.request_codename
        )
        return res


SiteSchema.update_forward_refs()
class LoginSchema(BaseModel):
    username:str
    password:str