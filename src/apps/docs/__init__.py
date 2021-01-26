import os

from fastapi import FastAPI
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from src import settings
from src.common import get_file_content
from src.settings import BASE_DIR

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "realman/templates"))


@app.get("/enums")
async def enums(request: Request):
    enums_content = get_file_content(os.path.join(settings.BASE_DIR, "src/enums/db.py"))
    return templates.TemplateResponse(
        "enums.html", {"request": request, "enums_content": enums_content}
    )


@app.get("/errors")
async def errors(request: Request):
    errors_content = get_file_content(os.path.join(settings.BASE_DIR, "src/apps/api/errors.py"))
    return templates.TemplateResponse(
        "errors.html", {"request": request, "errors_content": errors_content}
    )


@app.get("/models")
async def models(request: Request):
    models_content = get_file_content(os.path.join(settings.BASE_DIR, "src/models.py"))
    return templates.TemplateResponse(
        "models.html", {"request": request, "models_content": models_content}
    )
