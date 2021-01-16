# -*- encoding: utf-8 -*-
"""
@File    : settings.py
@Time    : 2020/12/20 23:34
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import os
import sys

from . import global_settings

FASTAPI_VARIABLE = "FASTAPI_SETTINGS_MODULE"
import importlib


class Settings:
    def __init__(self):
        settings_module = os.environ.get(FASTAPI_VARIABLE)
        if not settings_module:
            work_path = os.getcwd()
            path_list = os.path.split(work_path)
            if path_list[-1] == "fast-tmp":
                settings_module = "example.settings"
            elif not os.path.isfile(
                os.path.join(path_list[-1], path_list[-1].replate("-", "_"), "settings.py")
            ):
                raise ImportError(
                    "未找到settings.py"
                    f"你必须设置环境变量{FASTAPI_VARIABLE}=你的settings.py的位置"
                    "或者在工作目录增加一个与工作目录同名的子目录并在里面增加settings.py"
                )
            else:
                settings_module = path_list[-1].replace("-", "_") + ".settings"
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))
        self.SETTINGS_MODULE = settings_module
        mod = importlib.import_module(self.SETTINGS_MODULE)
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
        if not getattr(self, "SECRET_KEY"):
            raise AttributeError("The SECRET_KEY setting must not be empty.")
        # fixme:时间处理??


settings = Settings()
