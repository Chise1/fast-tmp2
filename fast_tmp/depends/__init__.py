# -*- encoding: utf-8 -*-
"""
@File    : __init__.py.py
@Time    : 2021/1/18 10:10
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from .auth import authenticate_user, get_current_active_user, get_superuser, get_user_has_perms
from .pageing import PageDepend, page_depend
