from typing import Iterable, List, Type, Union

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()

group_permission = Table(
    "group_permission",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id")),
    Column("permission_code", String(128), ForeignKey("permission.code")),
)

group_user = Table(
    "group_user",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id")),
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id"),
    ),
)


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class User(BaseModel):
    __tablename__ = "user"

    username = Column(String(30))
    password = Column(String(128), nullable=True)
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

    async def has_perm(self, perm: str) -> bool:
        """
        判定用户是否有权限
        """
        pass

    async def has_perms(self, perms: Iterable[str]) -> bool:
        """
        根据permission的codename进行判定
        """

    async def get_perms(self) -> List[str]:
        pass

    def __str__(self):
        return self.username


#
#
class Group(BaseModel):
    __tablename__ = "group"
    name = Column(String(32))
    permissions = relationship(
        "Permission", secondary="group_permission", backref="groups", cascade="all,delete"
    )
    users = relationship("User", secondary="group_user", backref="groups", cascade="all,delete")


class Permission(Base):
    __tablename__ = "permission"
    code = Column(String(128), primary_key=True)
    name = Column(String(128))

    def __str__(self):
        return self.name + "-" + self.code
