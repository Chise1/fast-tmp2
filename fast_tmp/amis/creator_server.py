# -*- encoding: utf-8 -*-
"""
@File    : creator_server.py
@Time    : 2021/1/18 15:43
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.models import AbstractModel


class CRUD_Server:
    """
    生成CRUD页面
    """

    def __init__(self, router: AmisRouter, title: str, base_path: str, model: AbstractModel):
        self.router = router
        tpl = CRUD_TPL(
            title,
            f"get:/{base_path}",
            get_columns_from_model(model),
        )
        tpl.add_create_button(
            f"post:/{base_path}",
            controls=get_controls_from_model(AbstractModel, exclude_pk=True),
        )
        tpl.add_delete_button("delete:/" + base_path + "/${id}")
        tpl.add_modify_button(
            get_api="get:/" + base_path + "/${id}",
            put_api="put:/" + base_path + "/${id}",
            controls=get_controls_from_model(model, exclude_pk=True),
        )
        router.registe_tpl(tpl)
        router.site_schema.icon = "fa fa-file"
        self.tpl = tpl
