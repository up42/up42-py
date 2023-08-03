from pystac_client import Client

from up42.auth import Auth

# pylint: skip-file


class pystac_auth_client(Client):
    def __init__(
        self, id="id", description="description", auth: Auth = None, *args, **kwargs
    ):
        super().__init__(id=id, description=description, *args, **kwargs)
        self.auth = auth

    def _auth_modifier(self, request):
        self.auth._get_token()
        request.headers["Authorization"] = f"Bearer {self.auth.token}"

    def open(self, *args, **kwargs) -> Client:
        return super().open(
            request_modifier=self._auth_modifier,
            *args,
            **kwargs,
        )
