# -*- encoding: utf-8 -*-
"""
@File    : test_utils.py
@Time    : 2021/2/16 9:20
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from example.models import Message
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.models import Group

x = get_columns_from_model(Message)
y = get_controls_from_model(Message)
print(x)
print(y)
z = get_controls_from_model(Group)
print(z)
