from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fast_tmp.amis_router import AmisRouter
from fast_tmp.db import get_db_session

hello_fast_tmp_router = AmisRouter(title="示例路由", prefix="/test")


@hello_fast_tmp_router.get("/hello")
async def hello_fast_mtp(session: AsyncSession = Depends(get_db_session)):
    return "你好,fast-tmp."
