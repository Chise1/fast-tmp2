# -*- encoding: utf-8 -*-
"""
@File    : schemas.py
@Time    : 2021/1/16 17:25
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import Optional, List, Union

from pydantic.main import BaseModel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator

from fast_tmp.models import Group, Permission

group_list_schema = pydantic_queryset_creator(Group, exclude=("permissions", "users"))
group_schema = pydantic_model_creator(Group,name='group_schema', exclude_readonly=True)

class GroupS(group_schema):
    permissions: Optional[List[int]]  # 增加额外的权限字段
    users: Optional[List[int]]

permission_list_schema = pydantic_queryset_creator(Permission, exclude=("groups",))


class GroupGetList(BaseModel):
    items: group_list_schema
    total: int
