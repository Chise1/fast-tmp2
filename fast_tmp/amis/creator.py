# -*- encoding: utf-8 -*-
"""
@File    : creator.py
@Time    : 2021/3/6 21:17
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :工具包
"""
import inspect
from typing import List, Optional

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.orm import Session
from starlette import status

from fast_tmp.amis_router import AmisRouter
from fast_tmp.db import get_db_session
from fast_tmp.models import AbstractModel


def add_filter(func, filters: List[str] = None):
    signature = inspect.signature(func)
    res = []
    for k, v in signature.parameters.items():
        if k == "kwargs":
            continue
        res.append(v)
    if filters:
        for filter_ in filters:
            res.append(
                inspect.Parameter(
                    filter_, kind=inspect.Parameter.KEYWORD_ONLY, annotation=str, default=None
                )
            )  # fixme:之后支持根据字段类型进行自定义
    func.__signature__ = inspect.Signature(parameters=res, __validate_parameters__=False)


# fixme:等待测试
def create_list_route(
    route: AmisRouter,
    path: str,
    model: AbstractModel,
    schema: BaseModel,
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
        total_query = session.query(func.count(model.id))
        query = select(model).limit(perPage).offset((page - 1) * perPage)
        search_query = None
        filter_query = None
        if search and searchs:  # fixme:等待测试
            search_query = or_(getattr(model, i).like(f"%{search}%") for i in searchs)
        if kwargs:
            s = []
            for k, v in kwargs.items():
                if v:
                    if v == "null_":
                        s.append(getattr(model, k) == None)
                    else:
                        s.append(getattr(model, k) == v)
                else:
                    pass
            if s:
                and_(*s)  # fixme:注意为空问题
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
        data = session.execute(query).scalars().all()
        return {"total": total_query.scalar(), "items": [schema.from_orm(i) for i in data]}

    add_filter(model_list, filters)
    route.get(path, codenames=codenames)(model_list)


# todo:增加一个retrieve的接口，

# fixme:等待测试
def create_delete_route(
    route: AmisRouter,
    path: str,
    model: AbstractModel,
    codenames: Optional[List[str]] = None,
):
    """
    删除路由生成器
    """

    def model_delete(
        id: int,
        session: Session = Depends(get_db_session),
    ):
        session.execute(delete(model).where(model.id == id))
        session.commit()
        return {  # fixme:amis不支持标准restful协议造成的
            "status": 0,
        }

    route.delete(path + "/${id}", codenames=codenames, status_code=status.HTTP_200_OK)(model_delete)


# fixme:等待测试
def create_post_route(
    route: AmisRouter,
    path: str,
    model: AbstractModel,
    schema: BaseModel,  # 不要有id
    codenames: Optional[List[str]] = None,
):
    def model_post(
        info: schema,
        session: Session = Depends(get_db_session),
    ):
        m = model(**info.dict())
        session.add(m)
        session.commit()
        return {"status": 0}

    route.post(
        path,
        codenames=codenames,
    )(model_post)


# fixme:等待测试
def create_put_route(
    route: AmisRouter,
    path: str,
    model: AbstractModel,
    schema: BaseModel,  # 不要有id
    codenames: Optional[List[str]] = None,
):
    def model_put(
        id: int,
        info: schema,
        session: Session = Depends(get_db_session),
    ):
        session.execute(update(model).where(model.id == id).values(**info.dict()))
        session.commit()
        return {"status": 0}

    route.put(path + "/${id}", codenames=codenames)(model_put)


def create_enum_route(
    route: AmisRouter,
    model: AbstractModel,
    path: str = "/enum-selects",
    label_name: str = None,
    codenames: Optional[List[str]] = None,
):
    """
    针对字段专门创建枚举路由
    """

    def column_get(
        column: str,
        session: Session = Depends(get_db_session),
    ):
        if column[-3:] == "_id":
            select_model = getattr(model, column[0:-3]).comparator.mapper.class_
        else:
            select_model = getattr(model, column).comparator.mapper.class_

        if label_name:
            results = session.execute(
                select(select_model.id, getattr(select_model, label_name))
            ).all()
            return [{"value": result[0], "label": result[1]} for result in results]
        else:
            results = session.execute(select(select_model.id)).all()  # fixme；先不考虑返回字段的枚举值
            return [{"value": result, "label": result} for result in results]

    route.get(path, codenames=codenames)(column_get)
