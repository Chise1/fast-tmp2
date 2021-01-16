from fastapi import Depends
from pydantic.main import BaseModel
from fast_tmp.amis_router import AmisRouter
from fast_tmp.api.schemas import permission_list_schema
from fast_tmp.depends import get_superuser
from fast_tmp.models import Permission, User

permission_router = AmisRouter(title="权限")


class PermissionList(
    BaseModel,
):
    items: permission_list_schema
    total: int


@permission_router.get(
    "/permission", response_model=PermissionList,
                       )
async def get_permissions(user: User = Depends(get_superuser)):
    return {"items": await Permission.all(), "total": await Permission.all().count()}
