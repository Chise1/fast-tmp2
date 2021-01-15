# -*- encoding: utf-8 -*-
"""
@File    : tpl.py
@Time    : 2021/1/15 0:37
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import List, Any, Dict, Union

from pydantic import BaseModel

from fast_tmp.amis.schema.abstract_schema import ApiUrl
from fast_tmp.amis.schema.actions import DialogAction
from fast_tmp.amis.schema.buttons import Operation
from fast_tmp.amis.schema.crud import CRUD
from fast_tmp.amis.schema.forms import Column, AbstractControl, Form
from fast_tmp.amis.schema.frame import Dialog
from fast_tmp.amis.utils import has_perms

need_check_route_type_api = ['crud', ]


def check_perms(user_codenames, need_codenames):
    for need_codename in need_codenames:
        for user_codename in user_codenames:
            if user_codename == need_codename:
                break
        else:
            return False
    return True


def update_route(
    request_codename: Dict[str, Dict[str, List[str]]],
    view: dict,
    is_superuser: bool,
    user_codenames: List[str],
    base_url: str
):
    for k, v in view.items():
        if k == 'type' and v in need_check_route_type_api:
            api = view['api']  # todo:需要兼容所有的路由格式
            assert len(api) > 1, "请输入路由"
            if len(api) < 3:
                path = api
                method = "get"
            elif api[0:3] == 'get':
                path = api[4:]
                method = "get"
            elif api[0:3].lower() == 'pos':
                path = api[5:]
                method = "post"
            elif api[0:3].lower() == 'put':
                path = api[4:]
                method = "put"
            elif api[0:3].lower == "pat":
                path = api[6:]
                method = "patch"
            else:
                raise ValueError(f"路由错误:{v}")
            if request_codename.get(path):
                codenames = request_codename.get(path).get(method)
                if codenames:
                    if not is_superuser and not check_perms(user_codenames, codenames):
                        return None
            view['api'] = method + ":" + base_url + path
        elif k == 'body':
            if isinstance(v, dict):
                x = update_route(request_codename, v, is_superuser, user_codenames, base_url)
                if not x:
                    return None
                view[k] = x
            elif isinstance(v, list):
                body_l = []
                for vi in v:
                    x = update_route(request_codename, vi, is_superuser, user_codenames, base_url)
                    if x:
                        body_l.append(x)
                if not body_l:
                    return None
                view[k] = body_l
    return view


class TPL():
    def get_view_dict(self, codenames: List[str], is_superuser: bool, server_url,
                      request_codename: Dict[
                          str, List[Dict[str, List[str]]]]):
        raise Exception("尚未实现")


class CRUD_TPL(TPL):
    views: List[BaseModel] = []  # 额外的控件
    operation_actions: [BaseModel] = []  # 列表内按钮控件
    crud: CRUD
    head: List[BaseModel]  # 所有信息参考page组件
    body: List[BaseModel]  # 在crud后面的组件
    __init = False

    def __init__(self, crud_name: str, api: str, columns: List[Column]):
        method = api.split(":")[0]
        if method not in ['get', 'post', 'put', 'patch']:
            raise ValueError("api格式不正确，请输入get:/xxx传输")
        self.crud = CRUD(api=api, columns=columns)
        self.name = crud_name

    # def add_action(self, action: Actions_P):
    #     self.body.append(action)
    #
    # def add_action_in_column(self, actions_p: Actions_P):
    #     self.operation_actions.append(actions_p)
    #
    # def add_delete_many_button(self, ):
    #     """
    #     批量删除
    #     :return:
    #     """
    #     pass
    #
    # def add_update_many_button(self, ):
    #     """
    #     批量更新
    #     :return:
    #     """
    #     pass
    #
    # def add_create_button(self, api: str, controls: List[AbstractControl], codenames: List[str]):
    #     url = ApiUrl(api)
    #     self.views.append(
    #         Actions_P(
    #             codenames=codenames,
    #             action=DialogAction(
    #                 label="新增",
    #                 dialog=Dialog(
    #                     title="新增",
    #                     body=Form(
    #                         name=f"新增{self.name}",
    #                         controls=controls,
    #                         api=url,
    #                     ),
    #                 ),
    #             )
    #         )
    #     )
    #     self.routes.append(url)

    def get_view_dict(self, user_codenames: List[str], is_superuser: bool, server_url: str,
                      request_codename: Dict[str, Dict[str, List[str]]]):
        # 先获取字典，再轮询字典所有子类，检查是否具有api，
        # 如果有api，判定是否符合权限，符合权限则返回，不符合则删除该节点
        res_views = []
        res_crud = None
        res_view = self.crud.dict()
        if res_view:
            return update_route(request_codename, res_view, is_superuser, user_codenames,
                                server_url)
        else:
            return None
