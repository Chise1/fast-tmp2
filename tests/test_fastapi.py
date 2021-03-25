# -*- encoding: utf-8 -*-
"""
@File    : test_fastapi.py
@Time    : 2021/1/12 9:43
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import json
import time
import typing
from base64 import b64decode, b64encode

import itsdangerous
from fastapi import APIRouter, Depends, FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from itsdangerous import BadTimeSignature, SignatureExpired
from starlette.requests import HTTPConnection, Request
from starlette.responses import HTMLResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

app = FastAPI()

import typing
from urllib.parse import quote_plus

from starlette.background import BackgroundTask
from starlette.datastructures import URL


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


async def red(request: Request):
    raise FastTmpRedirectResponse(request.url_for("test"))


@app.get("/test")
async def test():
    print("test")
    pass


@app.get("/t2")
async def test(r=Depends(red)):
    print("red")


cas_client = CASClient(
    version=3,
    service_url=settings.CAS_SERVICE_URL,
    server_url=settings.SERVER_URL
    # service_url='http://127.0.0.1:8002/login?next=%2Fprofile',
    # server_url='http://127.0.0.1:8000/cas/'
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.scope.get("path") == settings.CAS_LOGIN_URL:  # cas服务
        next = request.query_params.get("next", "/")
        if request.session.get("user", None):
            return RedirectResponse(request.url_for(next))
        elif ticket := request.query_params.get("ticket"):
            user, attributes, pgtiou = cas_client.verify_ticket(ticket)
            if not user:
                return HTMLResponse('Failed to verify ticket. <a href="/login">Login</a>')
            else:  # Login successfully, redirect according `next` query parameter.
                response = RedirectResponse(next)
                request.session["user"] = dict(user=user)
                return response
        else:
            cas_client.service_url = str(request.base_url) + "?" + "next=" + next
            cas_login_url = cas_client.get_login_url()
            return RedirectResponse(cas_login_url)
    elif request.scope.get("path") == settings.CAS_LOGOUT_URL:

        redirect_url = request.url_for(settings.CAS_LOGOUT_CALLBACK_URL)
        redirect_url += "?next="
        cas_logout_url = cas_client.get_logout_url(redirect_url)
        return RedirectResponse(cas_logout_url)
    elif request.scope.get("path") == settings.CAS_LOGOUT_CALLBACK_URL:
        request.session.pop("user", None)
        return settings.HOME_URL
    else:
        response = await call_next(request)
        return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8003)
