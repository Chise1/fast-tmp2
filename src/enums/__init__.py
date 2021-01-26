from fast_tmp.utils.base_enums import CharEnumType, IntEnumType


class Status(IntEnumType):
    """
    状态
    """

    on = 1, "开启"
    off = 0, "关闭"


class Status2(CharEnumType):
    """
    状态
    """

    on = "on", "开启"
    off = "off", "关闭"
