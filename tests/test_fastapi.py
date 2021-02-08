# -*- encoding: utf-8 -*-
"""
@File    : test_fastapi.py
@Time    : 2021/1/12 9:43
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import HTTPException

app = FastAPI()


@app.get("/test")
async def test():
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
