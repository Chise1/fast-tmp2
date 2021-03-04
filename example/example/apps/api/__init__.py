from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings
from example.apps.api.routes.hello_fast_tmp import hello_fast_tmp_router
from .routes.amis_html import router as amis_router
example_app = AmisAPI(
    title="api",
    debug=settings.DEBUG,
)
example_app.include_router(hello_fast_tmp_router)
example_app.include_router(amis_router)