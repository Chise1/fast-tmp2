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
from typing import List, Optional, Union

from pydantic.main import BaseModel


class PermissionPageType(str, Enum):
    page = "page"
    widget = "widget"
    route = "route"


class PermissionSchema(BaseModel):
    label: str
    codename: str = None
    type: PermissionPageType = PermissionPageType.widget
    children: List[Union["PermissionSchema", "SiteSchema"]] = []
    url: str = ""  # 基础理由
    has_view: bool = False


class SiteSchema(PermissionSchema):
    icon: Optional[str]
    schema_api: str = "/schema_api"
    link: Optional[str]
    redirect: Optional[str]
    rewrite: bool = False
    visable: bool = True
