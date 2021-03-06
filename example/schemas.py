# 这里主要保存根据model生成的schema
from typing import Any, List

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from example.models import Message, MessageUser
from fast_tmp.models import Permission, User

message_schema = sqlalchemy_to_pydantic(Message)
user_schema = sqlalchemy_to_pydantic(User)
permission_schema = sqlalchemy_to_pydantic(Permission)


class ResMessageList(BaseModel):
    total: int
    items: List[message_schema]
