# -*- encoding: utf-8 -*-
"""
@File    : creator.py
@Time    : 2021/3/6 21:17
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :工具包
"""
from typing import List

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from example.schemas import message_schema
from fast_tmp.amis_router import AmisRouter
from fast_tmp.db import get_db_session
from fast_tmp.models import AbstractModel


def create_list_route(
    route: AmisRouter, path: str, model: AbstractModel, schema: message_schema, codenames: List[str]
):
    """
    创建list的路由
    """

    def model_list(
        page: int = 1,
        perPage: int = 10,
        session: Session = Depends(get_db_session),
    ):
        total = session.execute(func.count(model.id)).first()[0]
        data = (
            session.execute(select(model).limit(perPage).offset((page - 1) * perPage))
            .scalars()
            .all()
        )
        return {"total": total, "items": [schema.from_orm(i) for i in data]}

    route.get(path, codenames=codenames)(model_list)
