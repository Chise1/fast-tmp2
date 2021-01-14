from fastapi import Form, HTTPException
from starlette import status
from starlette.requests import Request

from fast_tmp.amis_router import AmisRouter
from fast_tmp.conf import settings
from fast_tmp.depends import authenticate_user
from fast_tmp.templates_app import templates
from fast_tmp.utils.token import create_access_token

user_router = AmisRouter(title="用户", prefix="/user")


@user_router.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse(
        "gh-pages/login.html",
        {
            "request": request,
        },
    )


@user_router.post("/login")
async def login(
    request: Request,
    username: str = Form(
        ...,
    ),
    password: str = Form(
        ...,
    ),
):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=settings.EXPIRES_DELTA
    )
    return templates.TemplateResponse(
        "gh-pages/index.html",
        {"request": request, "access_token": access_token},
    )
