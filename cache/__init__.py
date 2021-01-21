import aioredis
from typing import Optional
from fast_tmp.conf import settings
from aioredis import Redis

# todo:考虑使用多种缓存后端
redis_con: Optional[Redis] = None


async def close():
    global redis_con
    if redis_con is not None:
        redis_con.close()
        await redis_con.wait_closed()


async def init():
    global redis_con
    redis_con = await aioredis.create_redis_pool((settings.REDIS_HOST, settings.REDIS_PORT), db=settings.REDIS_DB,
                                                 password=settings.REDIS_PASSWORD
                                                 )
def get_client():
    global redis_con
    return redis_con