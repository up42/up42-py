import requests

from up42.http import http_adapter

SCHEMAS = ["http", "https"]


class StatusValidatingSession(requests.Session):
    def request(self, *args, **kwargs) -> requests.Response:
        raise_for_status = kwargs.pop("raise_for_status", True)
        response = super().request(*args, **kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response


def create(
    auth: requests.auth.AuthBase,
    create_adapter=http_adapter.create,
) -> requests.Session:
    session = StatusValidatingSession()
    adapter = create_adapter()
    for schema in SCHEMAS:
        session.mount(schema + "://", adapter)
    session.auth = auth
    return session
