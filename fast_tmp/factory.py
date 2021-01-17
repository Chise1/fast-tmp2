import os
import sys

from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from fast_tmp.amis_app import AmisAPI
from fast_tmp.api import app as b_app
from fast_tmp.api.group import group_router
from fast_tmp.api.permission import permission_router
from fast_tmp.api.user import user_router
from fast_tmp.conf import settings
from fast_tmp.exception_handler import validation_exception_handler

paths = sys.path


def get_dir():
    return os.path.dirname(__file__)


DIR = get_dir()


def create_fast_tmp_app() -> AmisAPI:
    fast_tmp_app = AmisAPI(
        title="fast_tmp_bk",
        debug=settings.DEBUG,
    )
    if settings.DEBUG:
        fast_tmp_app.mount(
            "/static", StaticFiles(directory=os.path.join(DIR, "static")), name="static"
        )
    else:
        fast_tmp_app.mount(
            "/static",
            StaticFiles(directory=os.path.join(settings.BASE_DIR, settings.STATIC_ROOT)),
            name="static",
        )
    fast_tmp_app.include_router(b_app)
    fast_tmp_app.include_router(permission_router)
    fast_tmp_app.include_router(group_router)
    fast_tmp_app.include_router(user_router)
    # fast_tmp_app.include_router(auth_router)
    # fast_tmp_app.include_router(auth2_router)
    # fast_tmp_app.add_exception_handler(
    #     HTTPException, http_exception_handler
    # )
    # fast_tmp_app.add_exception_handler(
    #     ErrorException, error_exception_handler
    # )
    fast_tmp_app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )

    return fast_tmp_app
