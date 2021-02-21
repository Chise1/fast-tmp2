import typing
from urllib.parse import quote_plus

from fastapi import HTTPException
from starlette.background import BackgroundTask
from starlette.datastructures import URL
from starlette.responses import RedirectResponse


class LoginError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail={"code": 1, "msg": "账户或密码错误", "detail": ""},
            headers={"WWW-Authenticate": "Bearer"},
        )


class FastTmpRedirectResponse(RedirectResponse, HTTPException):
    """
    通过raise抛出跳转
    """

    def __init__(
        self,
        url: typing.Union[str, URL],
        status_code: int = 307,
        headers: dict = None,
        background: BackgroundTask = None,
    ) -> None:
        super(RedirectResponse, self).__init__(
            content=b"", status_code=status_code, headers=headers, background=background
        )
        super(HTTPException, self).__init__(status_code=status_code, detail=None)
        self.headers["location"] = quote_plus(str(url), safe=":/%#?&=@[]!$&'()*+,;")
