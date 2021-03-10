from example.apps.api.routes.hello_fast_tmp import hello_fast_tmp_router
from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings

from .routes.amis_html import router as amis_router
from .routes.crud_server import crud_server_route, crud_user_route

example_app = AmisAPI(
    title="api",
    debug=settings.DEBUG,
)
example_app.include_router(hello_fast_tmp_router)
example_app.include_router(amis_router)
example_app.include_router(crud_server_route)
example_app.include_router(crud_user_route)
