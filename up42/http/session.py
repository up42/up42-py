import functools

import requests

from up42.http import http_adapter, oauth

SCHEMAS = ["http", "https"]


class StatusValidatingSession(requests.Session):
    def request(self, *args, **kwargs) -> requests.Response:
        raise_for_status = kwargs.pop("raise_for_status", True)
        response = super().request(*args, **kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response


@functools.lru_cache
def create(
    create_adapter=http_adapter.create,
    create_auth=oauth.Up42Auth,
) -> requests.Session:
    session = StatusValidatingSession()
    adapter = create_adapter()
    for schema in SCHEMAS:
        session.mount(schema + "://", adapter)
    session.auth = create_auth(create_adapter=create_adapter)
    return session
