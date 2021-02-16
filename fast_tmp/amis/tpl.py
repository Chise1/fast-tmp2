# -*- encoding: utf-8 -*-
"""
@File    : tpl.py
@Time    : 2021/1/15 0:37
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import json
from typing import Dict, List

from pydantic import BaseModel

from fast_tmp.amis.schema.abstract_schema import _Action
from fast_tmp.amis.schema.actions import AjaxAction, DialogAction
from fast_tmp.amis.schema.buttons import Operation
from fast_tmp.amis.schema.crud import CRUD
from fast_tmp.amis.schema.enums import ButtonLevelEnum
from fast_tmp.amis.schema.forms import AbstractControl, AmisColumn, Form
from fast_tmp.amis.schema.frame import Dialog
from fast_tmp.amis.schema.page import Page

need_check_route_type_api = [
    "crud",
]


def check_perms(user_codenames, need_codenames):
    for need_codename in need_codenames:
        for user_codename in user_codenames:
            if user_codename == need_codename:
                break
        else:
            return False
    return True


def get_path_method(v):
    assert len(v) > 1, "请输入路由"
    if len(v) < 3:
        path = v
        method = "get"
    elif v[0:3] == "get":
        path = v[4:]
        method = "get"
    elif v[0:3].lower() == "pos":
        path = v[5:]
        method = "post"
    elif v[0:3].lower() == "put":
        path = v[4:]
        method = "put"
    elif v[0:3].lower() == "pat":
        path = v[6:]
        method = "patch"
    elif v[0:3].lower() == "del":
        path = v[7:]
        method = "delete"
    else:
        raise ValueError(f"路由错误:{v}")
    return path, method


def update_route(
    request_codename: Dict[str, Dict[str, List[str]]],
    view: dict,
    is_superuser: bool,
    user_codenames: List[str],
    base_url: str,
):
    if not view:
        return None
    for k, v in view.items():
        if (k.find("api") >= 0 or k.find("Api") >= 0 or k == "source") and v:  # todo:需要兼容所有的路由格式
            if isinstance(v, dict):
                path = v["url"]
                method = v["method"]
            else:
                path, method = get_path_method(v)
            if request_codename.get(path):
                codenames = request_codename.get(path).get(method)
                if codenames:
                    if not is_superuser and not check_perms(user_codenames, codenames):
                        return None
            view[k] = method + ":" + base_url + path
        elif k in ["body", "controls", "dialog"]:
            if isinstance(v, list):
                body_l = []
                for vi in v:
                    x = update_route(request_codename, vi, is_superuser, user_codenames, base_url)
                    if x:
                        body_l.append(x)
            else:
                body_l = update_route(request_codename, v, is_superuser, user_codenames, base_url)
            view[k] = body_l
    return view


class TPL:
    def get_view_dict(
        self,
        user_codenames: List[str],
        is_superuser: bool,
        server_url: str,
        request_codename: Dict[str, Dict[str, List[str]]],
    ):
        assert getattr(self, "json_view"), "请先设置json文件"
        body = []
        x = self._get_widget_dict(
            [self.json_view], user_codenames, is_superuser, server_url, request_codename
        )
        if x:
            body.append(x)

    def use_json_file(self, path: str):
        """
        导入json文件来实现
        :param path:
        :return:
        """
        with open(
            path,
        ) as f:
            self.json_view = json.load(f)

    def _get_widget_dict(
        self,
        view: List[BaseModel],
        user_codenames: List[str],
        is_superuser: bool,
        server_url: str,
        request_codename: Dict[str, Dict[str, List[str]]],
    ):
        x = []
        for view in view:
            view_dict = update_route(
                request_codename,
                view.dict(exclude_none=True),
                is_superuser,
                user_codenames,
                server_url,
            )
            if view_dict:
                x.append(view_dict)
        return x


class CRUD_TPL(TPL):
    views: List[BaseModel]  # 额外的控件
    operation_actions: [BaseModel]  # 列表内按钮控件
    crud: CRUD
    heads: List[BaseModel]  # 所有信息参考page组件
    body: List[BaseModel]  # 在crud后面的组件
    page: Page

    def __init__(self, crud_name: str, api: str, columns: List[AmisColumn]):
        self.views = []
        self.operation_actions = []
        self.heads = []
        self.body = []
        self.page = Page()
        method = api.split(":")[0]
        if method not in ["get", "post", "put", "patch"]:
            raise ValueError("api格式不正确，请输入get:/xxx传输")
        self.crud = CRUD(api=api, columns=columns)
        self.name = crud_name
        self.page.title = crud_name

    # def add_action(self, action: Actions_P):
    #     self.body.append(action)
    #
    def add_action_in_column(self, action: _Action):
        self.operation_actions.append(action)

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
    def add_delete_button(
        self,
        api: str,
    ):
        """
        注意：api要携带${id}，而不是python可识别的{id}
        """
        action = AjaxAction(
            api=api,
            label="删除",
            level=ButtonLevelEnum.danger,
        )
        self.add_action_in_column(action)

    def add_modify_button(self, get_api: str, put_api: str, controls: List[AbstractControl]):
        """
        增加一个修改按钮
        """
        self.add_action_in_column(
            DialogAction(
                label="修改",
                dialog=Dialog(
                    title="修改",
                    body=Form(
                        name=f"修改{self.name}",
                        controls=controls,
                        api=put_api,
                        initApi=get_api,
                    ),
                ),
            )
        )

    def add_create_button(self, api: str, controls: List[AbstractControl]):
        self.heads.append(
            DialogAction(
                label="新增",
                dialog=Dialog(
                    title="新增", body=Form(name=f"新增{self.name}", controls=controls, api=api)
                ),
            )
        )

    def get_view_dict(
        self,
        user_codenames: List[str],
        is_superuser: bool,
        server_url: str,
        request_codename: Dict[str, Dict[str, List[str]]],
    ):
        """
        把模型转为字典
        :param user_codenames:用户拥有的权限
        :param is_superuser: 用户是否为超管
        :param server_url: 基本路由
        :param request_codename: 从router获取到的权限
        :return:
        """
        # 先获取字典，再轮询字典所有子类，检查是否具有api，
        # 如果有api，判定是否符合权限，符合权限则返回，不符合则删除该节点
        page = self.page.dict(exclude_none=True)
        body = []
        if self.heads:
            x = self._get_widget_dict(
                self.heads, user_codenames, is_superuser, server_url, request_codename
            )
            if x:
                body.append(x)
        crud_view = self.crud.dict(exclude_none=True)
        if crud_view:
            r = update_route(
                request_codename,
                crud_view,
                is_superuser,
                user_codenames,
                server_url,
            )
            if r:
                if self.operation_actions:
                    operation = Operation().dict()
                    operation_actions = self._get_widget_dict(
                        self.operation_actions,
                        user_codenames,
                        is_superuser,
                        server_url,
                        request_codename,
                    )
                    if operation_actions:
                        operation["buttons"] = operation_actions
                        r["columns"].append(operation)
                body.append(r)
        if self.views:
            x = self._get_widget_dict(
                self.views, user_codenames, is_superuser, server_url, request_codename
            )
            if x:
                body.append(x)
        page["body"] = body
        return page
