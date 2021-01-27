import asyncio

from cache import close, get_client, init


async def base():
    await init()
    redis = get_client()

    await redis.set("my-key", "value")
    value = await redis.get("my-key", encoding="utf-8")
    print(value)
    await close()


# def test_cache():
#     asyncio.run(base())
