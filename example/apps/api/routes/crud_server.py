# -*- encoding: utf-8 -*-
"""
@File    : crud_server.py
@Time    : 2021/3/9 18:43
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from example.models import Message
from fast_tmp.amis.creator_server import CRUD_Server
from fast_tmp.amis_router import AmisRouter

crud_server_route = AmisRouter(title="server test", prefix="/server")


CRUD_Server(crud_server_route, base_path="server", model=Message)
