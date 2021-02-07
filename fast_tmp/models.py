from typing import List, Type, Union

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    password = Column(String(128))
    is_superuser = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)

    def set_password(self, raw_password: str):
        """
        设置密码
        """
        pass

    def verify_password(self, raw_password: str) -> bool:
        """
        验证密码
        """
        pass

    @property
    async def perms(self) -> List[str]:
        pass

    async def has_perm(self, perm) -> bool:
        """
        判定用户是否有权限
        """
        pass

    async def has_perms(self, perms) -> bool:
        """
        根据permission的codename进行判定
        """

    async def get_perms(self):
        pass

    def __str__(self):
        return self.username


# from tortoise import Model, fields
#
# from fast_tmp.utils.password import make_password, verify_password
#
#
# class Permission(Model):
#     label = fields.CharField(max_length=128)
#     codename = fields.CharField(max_length=128, unique=True)
#
#     @classmethod
#     def make_permission(
#         cls,
#         model: Type[BaseModel],
#     ):
#         """
#         生成model对应的权限
#         """
#         model_name = model.__name__
#         Permission.get_or_create(
#             defaults={
#                 "label": "can read " + model_name,
#                 "model": model_name,
#                 "codename": "can_read_" + model_name,
#             }
#         )
#         Permission.get_or_create(
#             defaults={
#                 "label": "can create " + model_name,
#                 "model": model_name,
#                 "codename": "can_create_" + model_name,
#             }
#         )
#         Permission.get_or_create(
#             defaults={
#                 "label": "can update " + model_name,
#                 "model": model_name,
#                 "codename": "can_update_" + model_name,
#             }
#         )
#         Permission.get_or_create(
#             defaults={
#                 "label": "can delete " + model_name,
#                 "model": model_name,
#                 "codename": "can_delete_" + model_name,
#             }
#         )
#
#     def __eq__(self, other) -> bool:
#         if other == self.codename or getattr(other, "codename",
#                                              None) == self.codename:
#             return True
#         return False
#
#     def __str__(self):
#         return self.label
#
#     def __repr__(self):
#         return self.label
#
#

#
#
# class Group(Model):
#     label = fields.CharField(max_length=128, unique=True)
#     permissions = fields.ManyToManyField("fast_tmp.Permission",
#                                          related_name="groups")
#     users: fields.ManyToManyRelation[User]
#
#     def __str__(self):
#         return self.label
#
#
# class Config(Model):
#     name = fields.CharField(max_length=64)
#     key = fields.CharField(max_length=64, unique=True)
#     value = fields.JSONField()
#
#     @classmethod
#     async def get_value(cls, key: str):
#         conf = await cls.filter(key=key).first()
#         if not conf:
#             return None
#         return conf.value
