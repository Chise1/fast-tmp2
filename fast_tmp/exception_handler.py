# -*- encoding: utf-8 -*-
"""
@File    : exception_handler.py
@Time    : 2021/1/2 11:19
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


# RequestValidationError
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            {
                "data": None,
                "errors": {error["loc"][1]: error["msg"] for error in exc.errors()},
                "msg": "",
                "status": 422,
            }
        ),
    )
