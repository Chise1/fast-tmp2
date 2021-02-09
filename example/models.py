from sqlalchemy import *
from fast_tmp.models import BaseModel
class MessageUser(BaseModel):
    __tablename__='message_user'
    nickname = Column(String(32))


class Message(BaseModel):
    __tablename__="message"
    info = Column(String(32))
    # error_info = fields.IntEnumField(Status)
    # error_info_str = fields.CharEnumField(Status2)
    # message_user = fields.ForeignKeyField("fast_tmp.MessageUser")
    # t1 = fields.JSONField()
