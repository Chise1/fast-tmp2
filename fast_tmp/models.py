from typing import Container, Iterable, List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import backref, declarative_base, joinedload, relationship

from fast_tmp.utils.password import make_password, verify_password

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

    username = Column(String(30), unique=True)
    password = Column(String(128), nullable=True)
    is_superuser = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)

    def set_password(self, raw_password: str):
        """
        设置密码
        :param raw_password:
        :return:
        """
        self.password = make_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """
        验证密码
        :param raw_password:
        :return:
        """
        return verify_password(raw_password, self.password)

    # todo:需要测试
    async def has_perm(self, db_session: AsyncSession, perm: str) -> bool:
        """
        判定用户是否有权限
        """
        results = await db_session.execute(
            func.count(Group.id)
            .where(Group.users == self.id)
            .where(Group.permissions.any(Permission.code == perm))
        )
        if results.fetchone()[0]:
            return True
        return False

    # todo:需要测试
    async def has_perms(self, db_session: AsyncSession, perms: Container[str]) -> bool:
        """
        根据permission的codename进行判定
        """
        results = await db_session.execute(
            func.count(Group.id)
            .where(Group.users == self.id)
            .where(Group.permissions.any(Permission.code == perms))
        )
        if results.fetchone()[0]:
            return True
        return False

    def __str__(self):
        return self.username


class Group(BaseModel):
    __tablename__ = "group"
    name = Column(String(32))
    permissions = relationship(
        "Permission", secondary="group_permission", backref="groups", cascade="all,delete"
    )
    users = relationship("User", secondary="group_user", backref="groups", cascade="all,delete")

    # todo:等待测试
    async def get_perms(self, db_session: AsyncSession) -> Container[str]:
        results = await db_session.execute(
            select(group_permission).where(group_permission.c.group_id == self.id)
        )
        permissions = results.fetchall()
        print(permissions)
        return [permission[1] for permission in permissions]

    async def get_users(self, session: AsyncSession) -> Container[User]:
        results = await session.execute(
            select(Group).options(joinedload(Group.users)).where(Group.id == self.id)
        )
        return results.scalars().first().users


class Permission(Base):
    __tablename__ = "permission"
    code = Column(String(128), primary_key=True)
    name = Column(String(128))

    def __str__(self):
        return self.name + "-" + self.code
