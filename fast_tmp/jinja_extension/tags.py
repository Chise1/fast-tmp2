import jinja2
from pydantic import typing

from fast_tmp.conf import settings


def register_tags(templates):
    env = templates.env

    @jinja2.contextfunction
    def static(context: dict, **path_params: typing.Any) -> str:
        request = context["request"]
        path = settings.STATIC_APP
        return request.url_for(path, **path_params)  # fixme:因为空url会导致报错，目前无法把static通过nginx代理？？

    env.globals["static"] = static
