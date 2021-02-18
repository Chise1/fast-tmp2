# -*- encoding: utf-8 -*-
"""
@File    : oidc.py
@Time    : 2021/2/17 19:20
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import json

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret2")

config = Config(".env.cp")
config.environ["T1_CLIENT_ID"] = "568052"
config.environ["T1_CLIENT_SECRET"] = "ed107baa729189bdb710c1532b34db97a5f721c9bf5802cb139b875f"
oauth = OAuth(config)
CONF_URL = "http://127.0.0.1:8000/.well-known/openid-configuration"
oauth.register(name="t1", server_metadata_url=CONF_URL, client_kwargs={"scope": "openid"})


@app.route("/")
async def homepage(request: Request):
    user = request.session.get("user")
    if user:
        data = json.dumps(user)
        html = f"<pre>{data}</pre>" '<a href="/logout">logout</a>'
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.route("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.t1.authorize_redirect(request, redirect_uri)


@app.route("/auth")
async def auth(request: Request):
    try:
        token = await oauth.t1.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>{error.error}</h1>")
    user = await oauth.t1.parse_id_token(request, token)
    request.session["user"] = dict(user)
    return RedirectResponse(url="/")


@app.route("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
