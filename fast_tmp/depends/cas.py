import importlib
from typing import Any, List, Optional

from cas import CASClient
from fastapi import Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette.requests import Request

from fast_tmp.conf import settings
from fast_tmp.models import User
from fast_tmp.responses import FastTmpRedirectResponse
from fast_tmp.utils.token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.FAST_TMP_URL + "/auth/token")

cas_client = CASClient(
    version=3,
    service_url=settings.CAS_LOGIN_URL,
    server_url=settings.CAS_SERVER_URL,
)


async def cas_get_username(request: Request) -> str:
    """
    获取用户
    """
    user = request.session.get("cas_user", None)
    if not user:
        raise FastTmpRedirectResponse(
            f"{request.base_url}{settings.CAS_LOGIN_URL[1:]}?next={request.url}"
        )
    return user["user"]


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
                request.session["cas_user"] = dict(user=user)  # 需要增加检查该用户是否在数据库存在，并创建对应用户的方法
                module_paths = settings.CAS_CHECK_USER.split(".")
                x = importlib.import_module(".".join(module_paths[0:-1]))
                await getattr(x, module_paths[-1])(user["user"])
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


async def get_user(username: str = Depends(cas_get_username)) -> Optional[User]:
    user = await User.filter(username=username).first()
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_superuser(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user


def get_user_has_perms(perms: List[Any]):
    """
    判定用户是否具有相关权限
    """

    async def user_has_perms(user: User = Depends(get_current_active_user)):
        if await user.has_perms(perms):
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return user_has_perms
