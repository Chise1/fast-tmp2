from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from fast_tmp.amis_router import AmisRouter
from fast_tmp.api.user import user_router
from fast_tmp.conf import settings
from fast_tmp.depends import authenticate_user
from fast_tmp.utils.token import create_access_token

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.EXPIRES_DELTA
app = AmisRouter(title="fast_tmp", prefix="/auth", tags=["auth"])
from fastapi.responses import JSONResponse

app.include_router(user_router, prefix="/t")


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
    access_token_expires = ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/login",
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
