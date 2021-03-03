from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings
from fast_t.apps.api.routes.hello_fast_tmp import hello_fast_tmp_router
fast_t_app = AmisAPI(
    title="api",
    debug=settings.DEBUG,
)
app.include_router(hello_fast_tmp_router)