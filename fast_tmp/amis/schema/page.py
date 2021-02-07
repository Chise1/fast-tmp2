from typing import List, Optional, Union

from fast_tmp.amis.schema.abstract_schema import BaseAmisModel

from .enums import TypeEnum


class Page(BaseAmisModel):
    type = TypeEnum.page
    title: Optional[str]
    subTitle: Optional[str]
    remark: Optional[str]
    aside: Optional[Union[BaseAmisModel, List[BaseAmisModel]]]
    toolbar: Optional[Union[BaseAmisModel, List[BaseAmisModel]]]
    body: List[BaseAmisModel] = []
    className: Optional[str]
    cssVars: Optional[str]
    initApi: Optional[str]  # 获取初始数据
    initFetch: bool = False  # 是否进行初始数据获取


class HBox(BaseAmisModel):
    type = TypeEnum.hbox
    className: str = "b-a bg-dark lter"
    columns: List[BaseAmisModel]
