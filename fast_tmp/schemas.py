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


from fast_tmp.amis.schema.page import Page


class PermissionSchema(BaseModel):
    label: str
    codename: Optional[List[str]]
    type: PermissionPageType = PermissionPageType.widget
    url: str = ""  # 基础理由
    view: Optional[BaseModel]


class SiteSchema(PermissionSchema):
    icon: Optional[str]
    schema_api: str = "/schema_api"
    link: Optional[str]
    redirect: Optional[str]
    rewrite: bool = False
    visable: bool = True
    page: Optional[Page]
    children: List[Union[PermissionSchema, "SiteSchema"]] = []
