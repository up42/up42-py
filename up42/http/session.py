from typing import Callable

import requests

from up42 import utils
from up42.http import http_adapter

SCHEMAS = ["http", "https"]
REPOSITORY_URL = "https://github.com/up42/up42-py"
HttpAdapterFactory = Callable[[], requests.adapters.HTTPAdapter]


class StatusValidatingSession(requests.Session):
    def request(self, *args, **kwargs) -> requests.Response:
        raise_for_status = kwargs.pop("raise_for_status", True)
        response = super().request(*args, **kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response


def create(
    auth: requests.auth.AuthBase,
    create_adapter: HttpAdapterFactory = http_adapter.create,
    version: str = utils.get_up42_py_version(),
) -> requests.Session:
    session = StatusValidatingSession()
    adapter = create_adapter()
    for schema in SCHEMAS:
        session.mount(schema + "://", adapter)
    session.auth = auth
    session.headers = {
        "Content-Type": "application/json",
        "cache-control": "no-cache",
        "User-Agent": f"up42-py/{version} ({REPOSITORY_URL})",
    }
    return session
