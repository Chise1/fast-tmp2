class ErrorException(Exception):
    pass


class UserBanedError(ErrorException):
    """
    用户被封禁
    """

    pass
