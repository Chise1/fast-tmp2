from pydantic import BaseModel


class BaseError(BaseModel):
    error: int
    msg: str


class EntityNotFound(BaseError):
    error = 1
    msg = "实体未找到"


class UserBaned(BaseError):
    error = 2
    msg = "你的账号已被冻结"


class EntityExists(BaseError):
    error = 3
    msg = "实体已存在"


class VerifyCodeError(BaseError):
    error = 4
    msg = "验证码错误"


class WxCodeError(BaseError):
    error = 5
    msg = "微信授权码错误"


class PriceError(BaseError):
    error = 6
    msg = "价格错误"


class BalanceNotEnough(BaseError):
    error = 7
    msg = "余额不足"


class CreateError(BaseError):
    error = 8
    msg = "创建失败"


class NeedBindAccount(BaseError):
    error = 9
    msg = "需要绑定账号"


class TimesNotEnough(BaseError):
    error = 10
    msg = "次数不足"


class UpdateError(BaseError):
    error = 11
    msg = "更新失败"


class DeleteError(BaseError):
    error = 12
    msg = "删除失败"


class ParamError(BaseError):
    error = 13
    msg = "参数错误"


class ReadError(BaseError):
    error = 14
    msg = "读取错误"


class SendVerifyCodeError(BaseError):
    error = 15
    msg = "发送验证码失败,请重试"


class TokenInvalid(BaseError):
    error = 16
    msg = "token无效"


class Forbidden(BaseError):
    error = 17
    msg = "无权访问"


class UnKnownError(BaseError):
    error = 18
    msg = "未知错误"


class FoundUserError(BaseError):
    error = 19
    msg = "找不到对应用户信息"


class YlBaseError(BaseModel):
    error: int
    message: str


class YlConnectTimeOut(YlBaseError):
    error = 1
    message: str = "连接服务器超时"


class YlTaskErr(YlBaseError):
    error = 2
    message = "无法创建该任务类型"


class SignError(BaseError):
    error = 20
    msg = "sign签名过期或错误"
