# -*- encoding: utf-8 -*-
"""
@File    : creator.py
@Time    : 2021/3/6 21:17
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :工具包
"""
from typing import List, Optional
import inspect
from fastapi import Depends
from sqlalchemy import func, select, or_, and_
from sqlalchemy.orm import Session

from example.schemas import message_schema
from fast_tmp.amis_router import AmisRouter
from fast_tmp.db import get_db_session
from fast_tmp.models import AbstractModel
import inspect


def add_filter(func, filters: List[str] = None):
    signature = inspect.signature(func)
    res = []
    # signature=inspect.Signature()
    for k, v in signature.parameters.items():
        if k == 'kwargs':
            continue
        res.append(v)
    if filters:
        for filter_ in filters:
            res.append(
                inspect.Parameter(
                    filter_, kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=str, default=None
                )
            )  # fixme:之后支持根据字段类型进行自定义
    func.__signature__ = inspect.Signature(
        parameters=res, __validate_parameters__=False
    )


def create_list_route(
    route: AmisRouter,
    path: str,
    model: AbstractModel,
    schema: message_schema,
    codenames: Optional[List[str]] = None,
    filters: Optional[List[str]] = None,
    searchs: Optional[List[str]] = None,
):
    """
    创建list的路由
    """

    def model_list(
        page: int = 1,
        perPage: int = 10,
        search: Optional[str] = None,
        session: Session = Depends(get_db_session),
        **kwargs,
    ):
        # total = session.execute(func.count(model.id)).first()[0]
        total_query = session.query(func.count(model.id))
        query = select(model).limit(perPage).offset((page - 1) * perPage)
        if search:  # fixme:等待测试
            search_query = or_(
                getattr(model, i).like(f'%{search}%') for i in searchs
            )
        else:
            search_query = None
        if kwargs:
            filter_query = and_(
                getattr(model, k) == v for k, v in kwargs.items()
            )
        else:
            filter_query = None
        if search_query is not None and filter_query is not None:
            query = query.where(and_(search_query, filter_query))
            total_query = total_query.where(and_(search_query, filter_query))
        else:
            if search_query is not None:
                query = query.where(search_query)
                total_query = total_query.where(search_query)
            if filter_query is not None:
                query = query.where(filter_query)
                total_query = total_query.where(filter_query)
        data = (
            session.execute(query).scalars().all()
        )
        return {"total": total_query.scalar(),
                "items": [schema.from_orm(i) for i in data]}

    add_filter(model_list, filters)
    route.get(path, codenames=codenames)(model_list)
