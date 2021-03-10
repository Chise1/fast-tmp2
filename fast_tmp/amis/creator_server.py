# -*- encoding: utf-8 -*-
"""
@File    : creator_server.py
@Time    : 2021/1/18 15:43
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from fast_tmp.amis.creator import (
    create_delete_route,
    create_enum_route,
    create_list_route,
    create_post_route,
    create_put_route,
)
from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.models import AbstractModel


class CRUD_Server:
    """
    生成CRUD页面
    """

    def __init__(self, router: AmisRouter, base_path: str, model: AbstractModel):
        self.router = router
        tpl = CRUD_TPL(
            router.title,
            f"get:/{base_path}",
            get_columns_from_model(model),
        )
        m = sqlalchemy_to_pydantic(model, pydantic_name="m1")
        create_list_route(
            router,
            "/" + base_path,
            model,
            m,
        )
        tpl.add_create_button(
            f"post:/{base_path}",
            controls=get_controls_from_model(model, exclude_pk=True),
        )
        create_post_route(
            router,
            "/" + base_path,
            model,
            sqlalchemy_to_pydantic(model, exclude=["id"], pydantic_name="m2"),
        )
        tpl.add_delete_button("delete:/" + base_path + "/${id}")
        create_delete_route(router, "/" + base_path, model)
        tpl.add_modify_button(
            get_api="get:/" + base_path + "/${id}",
            put_api="put:/" + base_path + "/${id}",
            controls=get_controls_from_model(model, exclude_pk=True),
        )
        create_put_route(router, "/" + base_path, model, m)
        create_enum_route(router, model, label_name="nickname")
        router.registe_tpl(tpl)
        router.site_schema.icon = "fa fa-file"
        self.tpl = tpl
