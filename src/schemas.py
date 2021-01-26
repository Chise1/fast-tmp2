# 这里主要保存根据model生成的schema
from pydantic import BaseModel
from pydantic.schema import schema
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from .models import Message

message_list_schema = pydantic_queryset_creator(Message)
message_schema = pydantic_model_creator(Message, name="MessageCreate", exclude_readonly=True)


class ResMessageList(BaseModel):
    items: message_list_schema
    total: int
