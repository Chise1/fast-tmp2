from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware

from example.apps.api.routes.t import t_route
from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings
from starlette.middleware.cors import CORSMiddleware
from fast_tmp import factory
from fast_tmp.depends.cas import cas_middleware
from .apps.api.routes.amis_html import router as amis_test_router
from example.apps.api import app as example_app
from fast_tmp.redis import AsyncRedisUtil


def init_app(main_app: Starlette):
    @main_app.on_event("startup")
    async def startup() -> None:
        await AsyncRedisUtil.init(**settings.REDIS)

    @main_app.on_event("shutdown")
    async def shutdown() -> None:
        await AsyncRedisUtil.close()


def create_app() -> AmisAPI:
    app = AmisAPI(title='fast_tmp example', debug=settings.DEBUG)
    settings.app = app

    r_app = factory.create_fast_tmp_app()
    app.mount(settings.FAST_TMP_URL, r_app)
    app.mount("/example", example_app)
    app.include_router(amis_test_router)
    app.include_router(t_route)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Sentry的插件
    # app.add_middleware(SentryAsgiMiddleware)
    app.middleware("http")(cas_middleware)
    app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SESSION_SECRET)
    init_app(app)
    return app
