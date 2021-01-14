
from fastapi import Depends
from starlette.requests import Request

from fast_tmp.amis_router import AmisRouter
from fast_tmp.models import User
from fast_tmp.schemas import PermissionSchema
from fast_tmp.depends import get_user_has_perms
from fast_tmp.templates_app import templates
from fastapi.responses import HTMLResponse
auth_router = AmisRouter(prefix="/auth")
@auth_router.get("/login",)
async def xlogin(request: Request,):
    return templates.TemplateResponse(
            "gh-pages/login.html",
            {
                "request": request,
            },  # fixme:ujson or orjson
        )
@auth_router.get("/index",)
async def xlogin(request: Request,):
    return templates.TemplateResponse(
            "gh-pages/index.html",
            {
                "request": request,
            },
        )
# @auth_router.get("/test_perm",
#                  permission_model=PermissionSchema(label="测试权限", codename=['test_perm'], url='/test_perm'))
# async def test_perm(user: User = Depends(get_user_has_perms("test_perm"))):
#     return {"code": 200}
