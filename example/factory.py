from fastapi.exceptions import RequestValidationError
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.applications import Starlette

from example import rearq
from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings
from starlette.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from fast_tmp.exception_handler import validation_exception_handler
from fast_tmp.redis import AsyncRedisUtil


@rearq.on_startup
async def on_startup():
    await AsyncRedisUtil.init(**settings.REDIS)
    await Tortoise.init(config=settings.TORTOISE_ORM)


@rearq.on_shutdown
async def on_shutdown():
    await AsyncRedisUtil.close()
    await Tortoise.close_connections()


def init_app(main_app: Starlette):
    @main_app.on_event("startup")
    async def startup() -> None:
        await AsyncRedisUtil.init(**settings.REDIS)
        await Tortoise.init(config=settings.TORTOISE_ORM)
        await rearq.init()

    @main_app.on_event("shutdown")
    async def shutdown() -> None:
        await AsyncRedisUtil.close()
        await Tortoise.close_connections()
        await rearq.close()


def create_app() -> AmisAPI:
    app = AmisAPI(title='fast_tmp example', debug=settings.DEBUG)
    settings.app = app
    Tortoise.init_models(settings.TORTOISE_ORM["apps"]["fast_tmp"]["models"], "fast_tmp")
    from fast_tmp import factory
    from .apps.api.routes.amis_html import router as amis_test_router
    from example.apps.api import app as example_app
    r_app = factory.create_fast_tmp_app()
    app.mount(settings.FAST_TMP_URL, r_app)
    app.mount("/example", example_app)
    app.include_router(amis_test_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Sentry的插件
    # app.add_middleware(SentryAsgiMiddleware)
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    init_app(app)
    return app
