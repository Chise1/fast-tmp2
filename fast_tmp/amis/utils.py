from typing import List, Optional, Tuple, Type

from pydantic.main import BaseModel
from pydantic.schema import schema
from tortoise import Model
from tortoise.fields import (
    BigIntField,
    BooleanField,
    CharField,
    DateField,
    DatetimeField,
    DecimalField,
    FloatField,
    IntField,
    JSONField,
    SmallIntField,
    TextField,
    TimeDeltaField,
    UUIDField,
)
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance

from fast_tmp.amis.schema.forms import Column
from fast_tmp.amis.schema.forms.enums import ControlEnum, FormWidgetSize, ItemModel
from fast_tmp.amis.schema.forms.widgets import (
    Control,
    DateItem,
    DatetimeItem,
    NumberItem,
    SelectItem,
    SelectOption,
    SwitchItem,
    TextItem,
    TimeItem,
    UuidItem,
)


def get_coulmns_from_pqc(
    list_schema: Type[BaseModel],
    include: Tuple[str, ...] = None,
    exclude: Tuple[str, ...] = None,
    add_type=False,
    extra_fields=None,
):
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_field:额外的自定义字段
    """
    model_name = list_schema.__name__
    json_models = schema([list_schema])["definitions"]
    res: List[Column] = []
    for json_model in json_models:
        if json_model == model_name:
            items = json_models[json_model]["items"]
            for k, v in items.items():
                if k == "$ref":
                    m = json_models[v.split("/")[-1]]
                    fields = m["properties"]
                    for field_name in fields:
                        if include:
                            if field_name not in include:
                                continue
                        elif exclude:
                            if field_name in exclude:
                                continue
                        if add_type:
                            res.append(
                                Control(
                                    name=field_name,
                                    label=fields[field_name]["title"],
                                    type=pf_2_jsf(fields[field_name]["type"]),
                                )
                            )
                        else:
                            res.append(Column(name=field_name, label=fields[field_name]["title"]))
    if extra_fields:
        res.append(*extra_fields)
    return res


def pf_2_jsf(field_type: str) -> str:
    """
    把python的字段类型转为js的类型
    """
    print(field_type)
    if field_type == "integer":
        return ControlEnum.number
    else:
        return ControlEnum.text


# fixme:等待修复
def get_coulmns_from_pmc(
    model_schema: Type[BaseModel],
    include: Tuple[str, ...] = None,
    exclude: Tuple[str, ...] = None,
    add_type: bool = False,
):
    """
    从pydantic_model_creator创建的schema获取字段
    """
    model_name = model_schema.__name__
    j1 = model_schema.schema()
    json_models = schema([model_schema])["definitions"]
    res: List[Column] = []
    for json_model in json_models:
        if json_model == model_name:
            items = json_models[json_model]["properties"]
            for k, v in items.items():
                if include:
                    if k not in include:
                        continue
                if exclude:
                    if k in exclude:
                        continue
                if add_type:
                    res.append(
                        Control(name=k, label=v["title"], type=pf_2_jsf(v.get("type") or "string"))
                    )
                else:
                    res.append(Column(name=k, label=v["title"]))
            break
    return res


def get_columns_from_list(
    fields: List[str],
) -> List[Column]:
    res = []
    for field in fields:
        res.append(Column(name=field, label=field))
    return res


def _get_base_attr(field_type) -> dict:
    return dict(
        className=field_type.kwargs.get("className", None),
        inputClassName=field_type.kwargs.get("inputClassName", None),
        labelClassName=field_type.kwargs.get("labelClassName", None),
        name=field_type.model_field_name,
        label=field_type.kwargs.get("verbose_name", field_type.model_field_name),
        labelRemark=field_type.kwargs.get("labelRemark", None),
        description=field_type.kwargs.get("description", None),
        placeholder=field_type.kwargs.get("placeholder", "请输入..."),
        inline=field_type.kwargs.get("placeholder", False),
        submitOnChange=field_type.kwargs.get("submitOnChange", False),
        disabled=field_type.kwargs.get("disabled", False),
        disableOn=field_type.kwargs.get("disableOn", None),
        # validations=field_type.kwargs.get("validations", None),
        # validationErrors=field_type.kwargs.get("validationErrors", None),
        required=field_type.kwargs.get("required", True),
        mode=field_type.kwargs.get("mode", ItemModel.normal),
        size=field_type.kwargs.get("size", FormWidgetSize.md),
        value=getattr(field_type, "default", field_type.kwargs.get("default", None)),
    )


def get_columns_from_model(
    model: Type[Model],
    include: List[str] = None,
    exclude: List[str] = None,
    add_type: bool = False,
    extra_fields: Optional[List[Column]] = None,
    exclude_readonly: bool = False,
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_field:额外的自定义字段
    """
    fields = model._meta.fields_map

    res = []
    for field, field_type in fields.items():
        if include and field not in include or exclude and field in exclude:
            continue
        if add_type:
            if exclude_readonly and field_type.pk:
                continue
            if isinstance(field_type, (IntField, SmallIntField, BigIntField)):
                if isinstance(field_type, IntEnumFieldInstance):
                    enum_type = field_type.enum_type
                    res.append(
                        SelectItem(
                            options=[
                                SelectOption(label=label, value=value)
                                for value, label in enum_type.choices.items()
                            ],
                            **_get_base_attr(field_type),
                        ),
                    )
                else:
                    res.append(
                        NumberItem(
                            min=field_type.kwargs.get("min", None)
                            or field_type.constraints.get("ge"),
                            max=field_type.kwargs.get("max", None)
                            or field_type.constraints.get("le"),
                            precision=field_type.kwargs.get("precision", 0),
                            step=field_type.kwargs.get("step", 1),
                            **_get_base_attr(field_type),
                            validations={
                                "minimum": field_type.kwargs.get("min", None)
                                or field_type.constraints.get("ge"),
                                "maximum": field_type.kwargs.get("max", None)
                                or field_type.constraints.get("le"),
                            },
                        ),
                    )
            elif isinstance(field_type, CharField):
                if isinstance(field_type, CharEnumFieldInstance):
                    enum_type = field_type.enum_type
                    res.append(
                        SelectItem(
                            options=[
                                SelectOption(label=label, value=value)
                                for value, label in enum_type.choices.items()
                            ],
                            **_get_base_attr(field_type),
                        ),
                    )
                else:
                    res.append(
                        TextItem(
                            **_get_base_attr(field_type),
                            validations={
                                "maxLength": field_type.kwargs.get("maxLength", None)
                                or field_type.max_length,
                            },
                        )
                    )
            # todo:等待完成,另，需要完成date
            elif isinstance(field_type, DatetimeField):
                res.append(
                    DatetimeItem(
                        **_get_base_attr(field_type),
                        format=field_type.kwargs.get("format", "YYYY-MM-DD HH:mm:ss"),
                        inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD HH:mm:ss"),
                    )
                )
            elif isinstance(field_type, DateField):
                res.append(
                    DateItem(
                        **_get_base_attr(field_type),
                        format=field_type.kwargs.get("format", "YYYY-MM-DD"),
                        inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD"),
                    )
                )
            elif isinstance(field_type, TimeDeltaField):
                res.append(
                    TimeItem(
                        **_get_base_attr(field_type),
                        format=field_type.kwargs.get("format", "HH:mm"),
                        inputFormat=field_type.kwargs.get("inputFormat", "HH:mm"),
                        # placeholder=field_type.kwargs.get('placeholder', "请选择时间"),
                        timeConstrainst=field_type.kwargs.get("timeConstrainst", False),
                    )
                )
            elif isinstance(field_type, CharEnumFieldInstance):
                print(field_type.enum_type)
            elif isinstance(field_type, BooleanField):

                res.append(
                    SwitchItem(
                        type="switch",
                        # **_get_base_attr(field_type),
                        name=field_type.model_field_name,
                        label="开关",
                        trueValue=field_type.kwargs.get("trueValue", True),
                        falseValue=field_type.kwargs.get("falseValue", False),
                    )
                )
            elif isinstance(field_type, FloatField):
                validation = {}
                if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
                    validation["minimum"] = field_type.kwargs.get(
                        "min", None
                    ) or field_type.constraints.get("ge")
                if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
                    validation["maximum"] = field_type.kwargs.get(
                        "max", None
                    ) or field_type.constraints.get("le")
                res.append(
                    NumberItem(
                        min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
                        max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
                        precision=field_type.kwargs.get("precision", None),
                        step=field_type.kwargs.get("step", 1),
                        showSteps=field_type.kwargs.get("showSteps", None),
                        **_get_base_attr(field_type),
                        validations=validation,
                    )
                )
            elif isinstance(field_type, DecimalField):
                validation = {}
                if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
                    validation["minimum"] = field_type.kwargs.get(
                        "min", None
                    ) or field_type.constraints.get("ge")
                if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
                    validation["maximum"] = field_type.kwargs.get(
                        "max", None
                    ) or field_type.constraints.get("le")
                res.append(
                    NumberItem(
                        min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
                        max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
                        precision=field_type.kwargs.get("precision", 2),
                        step=field_type.kwargs.get("step", 1),
                        showSteps=field_type.kwargs.get("showSteps", None),
                        **_get_base_attr(field_type),
                        validations=validation,
                    )
                )
            elif isinstance(field_type, JSONField):
                pass
            elif isinstance(field_type, TextField):
                res.append(
                    TextItem(
                        **_get_base_attr(field_type),
                    )
                )
            elif isinstance(field_type, UUIDField):
                res.append(
                    UuidItem(
                        **_get_base_attr(field_type), length=field_type.kwargs.get("length", None)
                    )
                )
        else:
            res.append(Column(name=field, label=field_type.kwargs.get("verbose_name", field)))
    if extra_fields:
        res.extend(extra_fields)
    return res
def has_perms(view, codenames: List[str]):
    for codename in view.codenames:
        for u_c in codenames:
            if u_c == codename:
                break
        else:
            return False
    return True
