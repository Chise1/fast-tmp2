# -*- encoding: utf-8 -*-
"""
@File    : file_tree.py
@Time    : 2021/1/26 16:00
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fast_tmp.amis_router import AmisRouter

file_tree_router = AmisRouter(title="文件树")

@file_tree_router.get("/tree")
async def get_tree():
    """
    获取文件树
    """
    DirTree