#
# from typing import List, Optional
#
# from pydantic.main import BaseModel
# from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
#
# from fast_tmp.models import Group, Permission, User
#
#
#
# group_list_schema = pydantic_queryset_creator(Group, exclude=("permissions", "users"))
# group_schema = pydantic_model_creator(Group, name="group_schema", exclude_readonly=True)
#
#
# class GroupS(group_schema):
#     permissions: Optional[List[int]]  # 增加额外的权限字段
#     users: Optional[List[int]]
#
#
# permission_list_schema = pydantic_queryset_creator(Permission, exclude=("groups",))
# permission_schema = pydantic_model_creator(
#     Permission, name="permission_schema", include=("id", "label", "codename")
# )
# permission_create_schema = pydantic_model_creator(
#     Permission, exclude_readonly=True, name="permission_create_schema"
# )
# user_list_schema = pydantic_model_creator(User, exclude=("groups",))
# user_schema = pydantic_model_creator(
#     User, name="user_schema", include=("id", "username", "password", "is_active", "is_superuser")
# )
# user_create_schema = pydantic_model_creator(
#     User, include=("username", "password", "is_active", "is_superuser"), name="user_create_schema"
# )
#
#
# class GroupGetList(BaseModel):
#     items: group_list_schema
#     total: int
from pydantic import BaseModel


class LoginR(BaseModel):
    username: str
    password: str
