from typing import Any

from starlette.responses import JSONResponse


# fixme:考虑以后使用Ojson或ujson提速


class AmisResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        res = {"status": 0, "msg": "", "data": content}
        return super().render(res)
