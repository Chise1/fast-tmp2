from fast_tmp.amis_router import AmisRouter

hello_fast_tmp_router = AmisRouter(title="示例路由", prefix="/test")


@hello_fast_tmp_router.get("/hello")
async def hello_fast_mtp():
    return "你好,fast-tmp."
