import enum
from copy import copy
from typing import Container, List, Mapping, Optional, Type

import sqlalchemy
from sqlalchemy import BigInteger, Boolean
from sqlalchemy import Column as SqlColumn
from sqlalchemy import DateTime, Enum, Integer, SmallInteger, String, inspect
from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.decl_api import DeclarativeMeta

from fast_tmp.amis.schema.forms import AmisColumn, AmisMapping, Control
from fast_tmp.amis.schema.forms.enums import FormWidgetSize, ItemModel
from fast_tmp.amis.schema.forms.widgets import (
    DateItem,
    DatetimeItem,
    NumberItem,
    PickerItem,
    SelectItem,
    SelectItemCanModifyItem,
    SelectOption,
    SwitchItem,
    TextItem,
    TimeItem,
    TransferItem,
    UuidItem,
)


def _get_base_attr(column: SqlColumn, **kwargs) -> dict:
    res = column.info.get("amis", {})
    default = getattr(column, "default", None)
    if default is not None:
        res["value"] = column.default
    res["name"] = column.key
    res["label"] = column.info.get("verbose_name", column.key)
    res["description"] = column.info.get(
        "description", getattr(column, "description", None) or None
    )
    required = column.info.get("required", None)
    if required is not None:
        res["required"] = column.info.get("required")
    else:
        if hasattr(column, "nullable"):
            res["required"] = not getattr(column, "nullable")  # 是否必填
        else:
            res["required"] = False
    res.update(kwargs)
    return res


def _create_control(column) -> Control:
    if control := column.info.get("Control"):
        return control
    if len(column.foreign_keys) > 0:
        # 存在外键
        return SelectItem(
            **_get_base_attr(column),
            source=f"get:/enum-selects?column={column.key}",
            multiple=True,
            extractValue=True,
            joinValues=False,
        )
    if isinstance(column.type, SmallInteger):
        return NumberItem(
            min=column.info.get("min", -32767),
            max=column.info.get("max", 32767),
            precision=column.info.get("precision", 0),
            step=column.info.get("step", 1),
            **_get_base_attr(column),
            validations={
                "minimum": column.info.get("min", -32767),
                "maximum": column.info.get("max", 32767),
            },
        )
    elif isinstance(column.type, BigInteger):
        return NumberItem(
            precision=column.info.get("precision", 0),
            step=column.info.get("step", 1),
            **_get_base_attr(column),
        )
    elif isinstance(column.type, Integer):  # 整数，短整数，长整数
        return NumberItem(
            min=column.info.get("min", -2147483647),
            max=column.info.get("max", 2147483647),
            precision=column.info.get("precision", 0),
            step=column.info.get("step", 1),
            **_get_base_attr(column),
            validations={
                "minimum": column.info.get("min", -2147483647),
                "maximum": column.info.get("max", 2147483647),
            },
        )
    # elif isinstance(column.type, Float):
    #     pass
    # elif isinstance(column.type, DECIMAL):
    #     pass
    # elif isinstance(column.type, ARRAY):
    #     pass
    elif isinstance(column.type, Boolean):  # 如果有默认值则渲染为switch，否则渲染为下拉
        if column.default is not None:
            return SwitchItem(type="switch", **_get_base_attr(column), value=column.defualt)
    # elif isinstance(column.type, VARBINARY):
    #     pass
    # elif isinstance(column.type, LargeBinary):
    #     pass
    # elif isinstance(column.type, Interval):
    #     pass
    # elif isinstance(column.type, Time):
    #     pass
    elif isinstance(column.type, DateTime):
        return DatetimeItem(
            **_get_base_attr(column),
            format=column.info.get("format", "YYYY-MM-DD HH:mm:ss"),
            inputFormat=column.info.get("inputFormat", "YYYY-MM-DD HH:mm:ss"),
        )

    elif isinstance(column.type, sqlalchemy.Date):
        return DateItem(
            **_get_base_attr(column),
            format=column.info.get("format", "YYYY-MM-DD"),
            inputFormat=column.info.get("inputFormat", "YYYY-MM-DD"),
        )
    # elif isinstance(column.type, JSON):
    #     pass
    elif isinstance(column.type, Enum):
        return SelectItem(
            options=[
                SelectOption(label=column.type.enum_class.__members__[value].value, value=value)
                for value in column.type.enum_class.__members__
            ],
            **_get_base_attr(column),
        )
    elif isinstance(column.type, sqlalchemy.Text):
        return TextItem(
            **_get_base_attr(column),
        )
    # elif isinstance(column.type, Unicode):
    #     pass
    elif isinstance(column.type, String):
        return TextItem(
            **_get_base_attr(column),
            validations={
                "maxLength": column.info.get("maxLength") or column.type.length,
            },
        )
    # elif isinstance(column.type, PickleType):
    #     pass
    else:
        raise Exception(f"Can't found this type:{column.type}")


def _create_column(column) -> AmisColumn:
    if column.info.get("AmisColumn"):
        return column.info.get("AmisColumn")
    if isinstance(column.type, Enum):
        members: Mapping = column.type.enum_class.__members__
        return AmisMapping(
            name=column.key,
            label=column.info.get("verbose_name", column.key),
            map={k: members[k].value for k in members},
        )
    else:
        return AmisColumn(name=column.key, label=column.info.get("verbose_name", column.key))


def get_controls_from_model(
    db_model: Type,
    *,
    include: Container[str] = (),
    exclude: Container[str] = (),
    exclude_pk: bool = False,
) -> List[Control]:
    mapper = inspect(db_model)
    res = []
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if (include and name not in include) or name in exclude:
                    continue
                column = attr.columns[0]
                if column.primary_key and exclude_pk:
                    continue
                res.append(_create_control(column))
            # python_type: Optional[type] = None
            #
            # if hasattr(column.type, "impl"):
            #     if hasattr(column.type.impl, "python_type"):
            #         python_type = column.type.impl.python_type
            # elif hasattr(column.type, "python_type"):
            #     python_type = column.type.python_type
            # assert python_type, f"Could not infer python_type for {column}"
        elif isinstance(attr, RelationshipProperty):
            continue  # fixme:先不考虑relactionship的字段
            # res.append(
            #     SelectItem(
            #         **_get_base_attr(attr),
            #         source=f"get:/{attr.key}-selects",
            #         multiple=True,
            #         extractValue=True,
            #         joinValues=False,
            #     )
            # )
    return res


def get_columns_from_model(
    db_model: Type,
    *,
    include: Container[str] = (),
    exclude: Container[str] = (),
) -> List[Control]:
    """

    从pydantic_queryset_creator创建的schema获取字段
    注意：多对多字段是无法显示的
    """
    mapper = inspect(db_model)
    res = []
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if (include and name not in include) or name in exclude:
                    continue
                column = attr.columns[0]
                res.append(_create_column(column))
    return res


# fixme:增加对所有输入参数进行排序并hash存储，如果调用过则读取缓存
# from typing import Set

#
# def get_controls_from_model(
#     model,
#     include: List[str] = None,
#     exclude: List[str] = None,
#     extra_fields: Optional[List[Column]] = None,
#     exclude_readonly: bool = False,
# ) -> List[Column]:
#     """
#     从pydantic_queryset_creator创建的schema获取字段
#     extra_field:额外的自定义字段
#     """
#     fields = model._meta.fields_map
#     res = []
#     for field, field_type in fields.items():
#         if include and field not in include or exclude and field in exclude:
#             continue
#         if exclude_readonly and field_type.pk:
#             continue
#         if isinstance(field_type, (IntField, SmallIntField, BigIntField)):
#             if isinstance(field_type, IntEnumFieldInstance):
#                 enum_type = field_type.enum_type
#                 res.append(
#                     SelectItem(
#                         options=[
#                             SelectOption(label=label, value=value)
#                             for value, label in enum_type.choices.items()
#                         ],
#                         **_get_base_attr(field_type),
#                     ),
#                 )
#             else:
#                 res.append(
#                     NumberItem(
#                         min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
#                         max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
#                         precision=field_type.kwargs.get("precision", 0),
#                         step=field_type.kwargs.get("step", 1),
#                         **_get_base_attr(field_type),
#                         validations={
#                             "minimum": field_type.kwargs.get("min", None)
#                                        or field_type.constraints.get("ge"),
#                             "maximum": field_type.kwargs.get("max", None)
#                                        or field_type.constraints.get("le"),
#                         },
#                     ),
#                 )
#         elif isinstance(field_type, sqlalchemy.String):
#             if isinstance(field_type, CharEnumFieldInstance):
#                 enum_type = field_type.enum_type
#                 res.append(
#                     SelectItem(
#                         options=[
#                             SelectOption(label=label, value=value)
#                             for value, label in enum_type.choices.items()
#                         ],
#                         **_get_base_attr(field_type),
#                     ),
#                 )
#             else:
#                 res.append(
#                     TextItem(
#                         **_get_base_attr(field_type),
#                         validations={
#                             "maxLength": field_type.kwargs.get("maxLength", None)
#                                          or field_type.max_length,
#                         },
#                     )
#                 )
#         # todo:等待完成,另，需要完成date
#         elif isinstance(field_type, DatetimeField):
#             res.append(
#                 DatetimeItem(
#                     **_get_base_attr(field_type),
#                     format=field_type.kwargs.get("format", "YYYY-MM-DD HH:mm:ss"),
#                     inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD HH:mm:ss"),
#                 )
#             )
#         elif isinstance(field_type, DateField):
#             res.append(
#                 DateItem(
#                     **_get_base_attr(field_type),
#                     format=field_type.kwargs.get("format", "YYYY-MM-DD"),
#                     inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD"),
#                 )
#             )
#         elif isinstance(field_type, TimeDeltaField):
#             res.append(
#                 TimeItem(
#                     **_get_base_attr(field_type),
#                     format=field_type.kwargs.get("format", "HH:mm"),
#                     inputFormat=field_type.kwargs.get("inputFormat", "HH:mm"),
#                     # placeholder=field_type.kwargs.get('placeholder', "请选择时间"),
#                     timeConstrainst=field_type.kwargs.get("timeConstrainst", False),
#                 )
#             )
#         elif isinstance(field_type, CharEnumFieldInstance):  # fixme:需要修复
#             print(field_type.enum_type)
#         elif isinstance(field_type, BooleanField):
#             res.append(
#                 SwitchItem(
#                     type="switch",
#                     # **_get_base_attr(field_type),
#                     name=field_type.model_field_name,
#                     label="开关",
#                     trueValue=field_type.kwargs.get("trueValue", True),
#                     falseValue=field_type.kwargs.get("falseValue", False),
#                 )
#             )
#         elif isinstance(field_type, FloatField):
#             validation = {}
#             if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
#                 validation["minimum"] = field_type.kwargs.get(
#                     "min", None
#                 ) or field_type.constraints.get("ge")
#             if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
#                 validation["maximum"] = field_type.kwargs.get(
#                     "max", None
#                 ) or field_type.constraints.get("le")
#             res.append(
#                 NumberItem(
#                     min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
#                     max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
#                     precision=field_type.kwargs.get("precision", None),
#                     step=field_type.kwargs.get("step", 1),
#                     showSteps=field_type.kwargs.get("showSteps", None),
#                     **_get_base_attr(field_type),
#                     validations=validation,
#                 )
#             )
#         elif isinstance(field_type, DecimalField):
#             validation = {}
#             if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
#                 validation["minimum"] = field_type.kwargs.get(
#                     "min", None
#                 ) or field_type.constraints.get("ge")
#             if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
#                 validation["maximum"] = field_type.kwargs.get(
#                     "max", None
#                 ) or field_type.constraints.get("le")
#             res.append(
#                 NumberItem(
#                     min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
#                     max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
#                     precision=field_type.kwargs.get("precision", 2),
#                     step=field_type.kwargs.get("step", 1),
#                     showSteps=field_type.kwargs.get("showSteps", None),
#                     **_get_base_attr(field_type),
#                     validations=validation,
#                 )
#             )
#         elif isinstance(field_type, JSONField):  # fixme:需要解决tortoise-orm字段问题
#             pass
#         elif isinstance(field_type, TextField):
#             res.append(
#                 TextItem(
#                     **_get_base_attr(field_type),
#                 )
#             )
#         elif isinstance(field_type, UUIDField):
#             res.append(
#                 UuidItem(**_get_base_attr(field_type), length=field_type.kwargs.get("length", None))
#             )
#         elif isinstance(field_type, ManyToManyFieldInstance):  # 多对多字段
#             res.append(
#                 SelectItem(
#                     **_get_base_attr(field_type, required=False),
#                     source=f"get:/{field_type.model_field_name}-selects",
#                     multiple=True,
#                     extractValue=True,
#                     joinValues=False,
#                 )
#             )
#         elif isinstance(field_type, BackwardFKRelation):
#             res.append(
#                 SelectItem(
#                     **_get_base_attr(field_type, required=False),
#                     source=f"get:/{field_type.model_field_name}-selects",
#                 )
#             )
#         elif isinstance(field_type, ForeignKeyFieldInstance):
#             res.append(
#                 SelectItem(
#                     **_get_base_attr(field_type, required=False),
#                     source=f"get:/{field_type.model_field_name}-selects",
#                 )
#             )
#         else:
#             raise ValueError(f"{field}字段的字段类型尚不支持!")
#     if extra_fields:
#         res.extend(extra_fields)
#     return res
#


def has_perms(view, codenames: Container[str]):
    for codename in view.codenames:
        for u_c in codenames:
            if u_c == codename:
                break
        else:
            return False
    return True


# def get_controls_from_model_v1(
#     model: Type[Model],
#     include: List[str] = None,
#     exclude: List[str] = None,
#     extra_fields: Optional[List[Column]] = None,
#     exclude_readonly: bool = False,
# ) -> List[Column]:
#     """
#     从pydantic_queryset_creator创建的schema获取字段
#     extra_field:额外的自定义字段
#     """
#     fields = model._meta.fields_map
#     res = []
#     for field, field_type in fields.items():
#         if include and field not in include or exclude and field in exclude:
#             continue
#         if exclude_readonly and field_type.pk:
#             continue
#         if isinstance(field_type, (IntField, SmallIntField, BigIntField)):
#             if isinstance(field_type, IntEnumFieldInstance):
#                 enum_type = field_type.enum_type
#                 res.append(
#                     SelectItem(
#                         options=[
#                             SelectOption(label=label, value=value)
#                             for value, label in enum_type.choices.items()
#                         ],
#                         **_get_base_attr(field_type),
#                     ),
#                 )
#             else:
#                 res.append(
#                     NumberItem(
#                         min=field_type.kwargs.get("min", None)
#                             or field_type.constraints.get("ge"),
#                         max=field_type.kwargs.get("max", None)
#                             or field_type.constraints.get("le"),
#                         precision=field_type.kwargs.get("precision", 0),
#                         step=field_type.kwargs.get("step", 1),
#                         **_get_base_attr(field_type),
#                         validations={
#                             "minimum": field_type.kwargs.get("min", None)
#                                        or field_type.constraints.get("ge"),
#                             "maximum": field_type.kwargs.get("max", None)
#                                        or field_type.constraints.get("le"),
#                         },
#                     ),
#                 )
#         elif isinstance(field_type, CharField):
#             if isinstance(field_type, CharEnumFieldInstance):
#                 enum_type = field_type.enum_type
#                 res.append(
#                     SelectItem(
#                         options=[
#                             SelectOption(label=label, value=value)
#                             for value, label in enum_type.choices.items()
#                         ],
#                         **_get_base_attr(field_type),
#                     ),
#                 )
#             else:
#                 res.append(
#                     TextItem(
#                         **_get_base_attr(field_type),
#                         validations={
#                             "maxLength": field_type.kwargs.get("maxLength", None)
#                                          or field_type.max_length,
#                         },
#                     )
#                 )
#         # todo:等待完成,另，需要完成date
#         elif isinstance(field_type, DatetimeField):
#             res.append(
#                 DatetimeItem(
#                     **_get_base_attr(field_type),
#                     format=field_type.kwargs.get("format", "YYYY-MM-DD HH:mm:ss"),
#                     inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD HH:mm:ss"),
#                 )
#             )
#         elif isinstance(field_type, DateField):
#             res.append(
#                 DateItem(
#                     **_get_base_attr(field_type),
#                     format=field_type.kwargs.get("format", "YYYY-MM-DD"),
#                     inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD"),
#                 )
#             )
#         elif isinstance(field_type, TimeDeltaField):
#             res.append(
#                 TimeItem(
#                     **_get_base_attr(field_type),
#                     format=field_type.kwargs.get("format", "HH:mm"),
#                     inputFormat=field_type.kwargs.get("inputFormat", "HH:mm"),
#                     # placeholder=field_type.kwargs.get('placeholder', "请选择时间"),
#                     timeConstrainst=field_type.kwargs.get("timeConstrainst", False),
#                 )
#             )
#         elif isinstance(field_type, CharEnumFieldInstance):  # fixme:需要修复
#             print(field_type.enum_type)
#         elif isinstance(field_type, BooleanField):
#             res.append(
#                 SwitchItem(
#                     type="switch",
#                     # **_get_base_attr(field_type),
#                     name=field_type.model_field_name,
#                     label="开关",
#                     trueValue=field_type.kwargs.get("trueValue", True),
#                     falseValue=field_type.kwargs.get("falseValue", False),
#                 )
#             )
#         elif isinstance(field_type, FloatField):
#             validation = {}
#             if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
#                 validation["minimum"] = field_type.kwargs.get(
#                     "min", None
#                 ) or field_type.constraints.get("ge")
#             if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
#                 validation["maximum"] = field_type.kwargs.get(
#                     "max", None
#                 ) or field_type.constraints.get("le")
#             res.append(
#                 NumberItem(
#                     min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
#                     max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
#                     precision=field_type.kwargs.get("precision", None),
#                     step=field_type.kwargs.get("step", 1),
#                     showSteps=field_type.kwargs.get("showSteps", None),
#                     **_get_base_attr(field_type),
#                     validations=validation,
#                 )
#             )
#         elif isinstance(field_type, DecimalField):
#             validation = {}
#             if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
#                 validation["minimum"] = field_type.kwargs.get(
#                     "min", None
#                 ) or field_type.constraints.get("ge")
#             if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
#                 validation["maximum"] = field_type.kwargs.get(
#                     "max", None
#                 ) or field_type.constraints.get("le")
#             res.append(
#                 NumberItem(
#                     min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
#                     max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
#                     precision=field_type.kwargs.get("precision", 2),
#                     step=field_type.kwargs.get("step", 1),
#                     showSteps=field_type.kwargs.get("showSteps", None),
#                     **_get_base_attr(field_type),
#                     validations=validation,
#                 )
#             )
#         elif isinstance(field_type, JSONField):  # fixme:需要解决tortoise-orm字段问题
#             pass
#         elif isinstance(field_type, TextField):
#             res.append(
#                 TextItem(
#                     **_get_base_attr(field_type),
#                 )
#             )
#         elif isinstance(field_type, UUIDField):
#             res.append(
#                 UuidItem(
#                     **_get_base_attr(field_type), length=field_type.kwargs.get("length", None)
#                 )
#             )
#         elif isinstance(field_type, ManyToManyFieldInstance):  # 多对多字段
#             res.append(
#                 SelectItem(
#                     **_get_base_attr(field_type, required=False),
#                     source=f"get:/{field_type.model_field_name}-selects",
#                     multiple=True,
#                     extractValue=True,
#                     joinValues=False,
#                 )
#             )
#         elif isinstance(field_type, BackwardFKRelation):
#             res.append(
#                 SelectItem(
#                     **_get_base_attr(field_type, required=False),
#                     source=f'get:/{field_type.model_field_name}-selects',
#                 )
#             )
#         elif isinstance(field_type, ForeignKeyFieldInstance):
#             res.append(
#                 SelectItem(
#                     **_get_base_attr(field_type, required=False),
#                     source=f'get:/{field_type.model_field_name}-selects',
#                 )
#             )
#         else:
#             raise ValueError(f"{field}字段的字段类型尚不支持!")
#     if extra_fields:
#         res.extend(extra_fields)
#     return res
