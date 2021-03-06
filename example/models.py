from sqlalchemy import *
from sqlalchemy.orm import relationship

# 如果要配置另外的数据库，还不太懂咋设计
from fast_tmp.models import AbstractModel, Base


class MessageUser(AbstractModel):
    __tablename__ = "message_user"
    nickname = Column(String(32))


import enum


class ExampleEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class Message(AbstractModel):
    __tablename__ = "message"
    info = Column(String(32))
    enum = Column(Enum(ExampleEnum))
    message_user_id = Column(
        ForeignKey("message_user.id"),
    )
    message_user = relationship("MessageUser", backref="messages", cascade="all,delete")
    # error_info = fields.IntEnumField(Status)
    # error_info_str = fields.CharEnumField(Status2)
    # message_user = fields.ForeignKeyField("fast_tmp.MessageUser")
    # t1 = fields.JSONField()
