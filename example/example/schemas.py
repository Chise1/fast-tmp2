# 这里主要保存根据model生成的schema
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from pydantic import BaseModel
from typing import List
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from example.models import Message, MessageUser
from pydantic import BaseModel

from fast_tmp.models import User, Permission

message_schema = sqlalchemy_to_pydantic(Message)
user_schema=sqlalchemy_to_pydantic(User)
permission_schema=sqlalchemy_to_pydantic(Permission)
class ResMessageList(BaseModel):
    total: int
    items: List[message_schema]
