# -*- encoding: utf-8 -*-
"""
@File    : __init__.py.py
@Time    : 2021/1/18 10:10
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from .auth import get_superuser, get_user_has_perms, get_current_active_user, authenticate_user
from .pageing import page_depend,PageDepend