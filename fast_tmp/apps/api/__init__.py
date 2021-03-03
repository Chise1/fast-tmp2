from datetime import timedelta

from fastapi import Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request

from fast_tmp.amis_router import AmisRouter
from fast_tmp.apps.api.schemas import LoginR
from fast_tmp.conf import settings
from fast_tmp.depends import authenticate_user, get_current_active_user
from fast_tmp.func import get_site_from_permissionschema, init_permission
from fast_tmp.models import Permission, User
from fast_tmp.responses import LoginError
from fast_tmp.templates_app import templates
from fast_tmp.utils.token import create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = settings.EXPIRES_DELTA
app = AmisRouter(title="fast_tmp", prefix="/auth", tags=["auth"])

INIT_PERMISSION = False


@app.post("/token", response_class=JSONResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    仅用于docs页面测试返回用
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.pk}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/get-token")
async def login(form_data: LoginR):
    """
    标准的请求接口
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise LoginError()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.pk}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_pages(user: User):
    global INIT_PERMISSION
    app = settings.app

    # 初始化permission
    if not INIT_PERMISSION:
        await init_permission(app.site_schema, list(await Permission.all()))
        INIT_PERMISSION = True
    permissions = await user.perms
    site = get_site_from_permissionschema(app.site_schema, permissions, "", user.is_superuser)
    if site:
        return [site]
    else:
        return []


@app.get("/index", summary="主页面")
async def index(request: Request):
    return templates.TemplateResponse(
        "gh-pages/index.html",
        {
            "request": request,
        },
    )


class L(BaseModel):
    username: str
    password: str


@app.post("/index", summary="登录")
async def index(request: Request, u: L):
    user = await authenticate_user(u.username, u.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=settings.EXPIRES_DELTA)
    )
    return {"access_token": access_token}


@app.get("/site", summary="获取目录")
async def get_site(user: User = Depends(get_current_active_user)):
    """
    获取左侧导航栏
    :param user:
    :return:
    """
    global INIT_PERMISSION
    app = settings.app

    # 初始化permission
    if not INIT_PERMISSION:
        await init_permission(app.site_schema, list(await Permission.all()))
        INIT_PERMISSION = True
    permissions = await user.perms
    site = get_site_from_permissionschema(app.site_schema, permissions, "", user.is_superuser)

    if site:
        return {"pages": [site]}
    else:
        return {"pages": []}
