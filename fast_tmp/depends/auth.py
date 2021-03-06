from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_tmp.apps.exceptions import credentials_exception
from fast_tmp.conf import settings
from fast_tmp.db import get_db_session
from fast_tmp.models import User
from fast_tmp.schemas import LoginSchema
from fast_tmp.utils.token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.FAST_TMP_URL + "/auth/token")


def get_username(token: str = Depends(oauth2_scheme)) -> str:
    """
    从token获取username
    """
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username


def get_user(
    username: str = Depends(get_username), session: Session = Depends(get_db_session)
) -> Optional[User]:
    """
    从数据库读取数据
    """
    return session.execute(select(User).where(User.username == username)).scalar_one_or_none()


def authenticate_user(
    logininfo: LoginSchema, session: Session = Depends(get_db_session)
) -> Optional[User]:
    """
    验证密码
    """
    user = get_user(logininfo.username, session)
    if not user:
        return None
    if not user.verify_password(logininfo.password):
        return None
    return user


def get_current_user(
    user: Optional[User] = Depends(get_user),
) -> User:
    """
    获取存在的用户
    """
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取活跃的用户
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_superuser(current_user: User = Depends(get_current_active_user)):
    """
    获取超级用户(该用户必须是活跃的)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user


def get_user_has_perms(perms: List[str]) -> Callable:  # fixme:需要测试
    """
    判定用户是否具有相关权限
    """

    def user_has_perms(
        user: User = Depends(get_current_active_user),
        session: Session = Depends(get_db_session),
    ) -> User:
        if user.has_perms(session, perms):
            return user
        else:
            raise credentials_exception

    return user_has_perms
