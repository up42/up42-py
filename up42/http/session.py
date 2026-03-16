import json
from collections.abc import Callable
from typing import TypeAlias

import requests

from up42 import constants, utils
from up42.http import http_adapter

SCHEMAS = ["http", "https"]
HttpAdapterFactory: TypeAlias = Callable[[], requests.adapters.HTTPAdapter]


def _raise_for_status(response: requests.Response) -> None:
    """Raises :class:`requests.HTTPError` with response body included in the message."""
    if 200 <= response.status_code < 400:
        return

    http_error_msg = ""
    if 400 <= response.status_code < 500:
        http_error_msg = (
            f"{response.status_code} Client Error for url: {response.url}"
        )
    elif 500 <= response.status_code < 600:
        http_error_msg = (
            f"{response.status_code} Server Error for url: {response.url}"
        )

    try:
        response_body = response.json()
        if response_body:
            http_error_msg += (
                f". Response body:\n{json.dumps(response_body, indent=2)}"
            )
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    raise requests.HTTPError(http_error_msg, response=response)


class StatusValidatingSession(requests.Session):
    def request(self, *args, **kwargs) -> requests.Response:
        raise_for_status = kwargs.pop("raise_for_status", True)
        response = super().request(*args, **kwargs)
        if raise_for_status:
            _raise_for_status(response)
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
        "User-Agent": f"up42-py/{version} ({constants.REPOSITORY_URL})",
    }
    return session
