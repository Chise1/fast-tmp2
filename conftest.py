import asyncio

import pytest
from tortoise import Tortoise, generate_schema_for_client


@pytest.fixture(scope="session")  # 配置全局默认线程，注意这个千万不能省
def event_loop():
    return asyncio.get_event_loop()


# 从settings里面粘贴出来并修改
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "mnbvcxz123",
                "database": "fasttmptest",
                "echo": True,
                "maxsize": 10,
            },
        },
    },
    "apps": {
        "fast_tmp": {
            "models": ["fast_tmp.models", "aerich.models", "example.models"],
            "default_connection": "default",
        },
    },
}


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    # await Tortoise.init(config=TORTOISE_ORM, _create_db=True)  # 注意，这里的配置是测试数据库
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"fast_tmp": ["fast_tmp.models", "aerich.models", "src.models"]},
    )

    # 创建数据库
    await generate_schema_for_client(Tortoise.get_connection("default"), safe=True)
    # 尝试删除所有数据库，在所有的数据操作完毕之后回调该方法删除数据库
    yield
    await Tortoise._drop_databases()  # 所有测试完毕销毁测试数据库，如果觉得每次都太慢的话可以重构这个函数
