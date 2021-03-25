from typing import Container, Optional

from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from fast_tmp.amis.creator import (
    create_delete_route,
    create_enum_route,
    create_list_route,
    create_post_route,
    create_put_route,
    create_retrieve_route,
)
from fast_tmp.amis.tpl import CRUD_TPL
from fast_tmp.amis.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.amis_router import AmisRouter
from fast_tmp.models import AbstractModel


class CRUD_Server:
    """
    生成CRUD页面
    """

    def __init__(
        self,
        router: AmisRouter,
        base_path: str,
        model: AbstractModel,
        filters: Optional[Container[str]] = None,
        searchs: Optional[Container[str]] = None,
    ):
        self.router = router
        tpl = CRUD_TPL(
            router.title,
            f"get:/{base_path}",
            get_columns_from_model(model),
        )
        create_list_route(
            router,
            "/" + base_path,
            model,
            sqlalchemy_to_pydantic(model, pydantic_name=model.__name__ + "list"),
            [model.__name__ + "_list"],
            filters,
            searchs,
        )
        create_retrieve_route(
            router,
            "/" + base_path,
            model,
            sqlalchemy_to_pydantic(model, pydantic_name=model.__name__ + "retrieve"),
            [model.__name__ + "_retrieve"],
        )
        tpl.add_create_button(
            f"post:/{base_path}",
            controls=get_controls_from_model(model, exclude_pk=True),
        )
        create_post_route(
            router,
            "/" + base_path,
            model,
            sqlalchemy_to_pydantic(model, exclude=["id"], pydantic_name=model.__name__ + "create"),
            [model.__name__ + "_create"],
        )
        tpl.add_delete_button("delete:/" + base_path + "/${id}")
        create_delete_route(router, "/" + base_path, model, [model.__name__ + "_delete"])
        tpl.add_modify_button(
            get_api="get:/" + base_path + "/${id}",
            put_api="put:/" + base_path + "/${id}",
            controls=get_controls_from_model(model, exclude_pk=True),
        )
        create_put_route(
            router,
            "/" + base_path,
            model,
            sqlalchemy_to_pydantic(model, exclude=["id"], pydantic_name=model.__name__ + "_put"),
            [model.__name__ + "put"],
        )
        create_enum_route(
            router, model, label_name="nickname", codenames=[model.__name__ + "_enum"]
        )
        router.registe_tpl(tpl)
        router.site_schema.icon = "fa fa-file"
        self.tpl = tpl
