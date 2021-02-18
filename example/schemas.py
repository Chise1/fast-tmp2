# 这里主要保存根据model生成的schema
from typing import List

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from example.models import Message, MessageUser
from pydantic import BaseModel

message_schema = sqlalchemy_to_pydantic(Message)


class ResMessageList(BaseModel):
    total: int
    items: List[message_schema]
