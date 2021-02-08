from typing import List, Type, Union, Iterable

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, UniqueConstraint, Table
from sqlalchemy.orm import declarative_base, relationship, backref

Base = declarative_base()
group_permission = Table(
    "group_permission",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id"), ),
    Column("permission_id", Integer, ForeignKey("permission.id"), ),
)
group_user = Table(
    "group_user",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id"), ),
    Column("user_id", Integer, ForeignKey("user.id"), ),
)


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


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)

    name = Column(String(32))
    permissions = relationship(
        "Permission", secondary=group_permission,
        backref=backref("groups", cascade="all, delete-orphan")
    )
    users = relationship(
        "User", secondary=group_user,
        backref=backref("groups", cascade="all, delete-orphan")
    )


class Permission(Base):
    __tablename__ = 'permission'
    id = Column(Integer, primary_key=True)
    code = Column(String(128), unique=True)
    name = Column(String(128))

    def __str__(self):
        return self.name + "-" + self.code
