from typing import Optional

from cas import CASClient
from fastapi import FastAPI

# from fast_tmp.responses import FastTmpRedirectResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from fast_tmp.conf import settings
from fast_tmp.responses import FastTmpRedirectResponse

cas_client = CASClient(
    version=3,
    # service_url="http://127.0.0.1:8002/cas-login",
    service_url=settings.CAS_LOGIN_URL,
    # server_url=settings.CAS_SERVER_URL
    # service_url='http://127.0.0.1:8002/login?next=%2Fprofile',
    server_url="http://127.0.0.1:8000/cas/",
)


# app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SECRET,
#                   session_cookie=settings.CAS_SESSION_COOKIE_NAME)


async def cas_get_user(request: Request):
    """
    获取用户
    """
    user = request.session.get("cas_user", None)
    if not user:
        print(f"{request.base_url}{settings.CAS_LOGIN_URL}?next={request.url}")
        raise FastTmpRedirectResponse(
            f"{request.base_url}{settings.CAS_LOGIN_URL[1:]}?next={request.url}"
            # request.url_for(settings.CAS_LOGIN_URL, next=request.url)
        )
    return user


async def cas_middleware(request: Request, call_next):
    if request.scope.get("path") == "/cas-login":  # cas服务
        next_url = request.query_params.get("next", "/")
        if request.session.get("cas_user", None):
            return RedirectResponse(next_url)
        elif ticket := request.query_params.get("ticket"):
            user, attributes, pgtiou = cas_client.verify_ticket(ticket)
            if not user:
                return HTMLResponse('Failed to verify ticket. <a href="/login">Login</a>')
            else:  # Login successfully, redirect according `next` query parameter.
                response = RedirectResponse(next_url)
                request.session["cas_user"] = dict(user=user)
                return response
        else:
            cas_client.service_url = (
                f"{request.base_url}{settings.CAS_LOGIN_URL[1:]}?next={next_url}"
            )
            cas_login_url = cas_client.get_login_url()
            return RedirectResponse(cas_login_url)
    elif request.scope.get("path") == settings.CAS_LOGOUT_URL:
        redirect_url = f"{request.base_url}{settings.CAS_LOGOUT_CALLBACK_URL[1:]}"
        cas_logout_url = cas_client.get_logout_url(redirect_url)
        return RedirectResponse(cas_logout_url)
    elif request.scope.get("path") == settings.CAS_LOGOUT_CALLBACK_URL:
        request.session.pop("cas_user", None)
        return RedirectResponse(f"{request.base_url}{settings.HOME_URL[1:]}")
    else:
        response = await call_next(request)
        return response
