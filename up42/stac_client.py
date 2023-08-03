from pystac_client import Client

from up42.auth import Auth


class pystac_auth_client(Client):
    def __init__(
        self, *args, id="id", description="description", auth: Auth = None, **kwargs
    ):  # pylint: disable=redefined-builtin
        super().__init__(id=id, description=description, *args, **kwargs)  # type: ignore
        self.auth = auth

    def _auth_modifier(self, request):
        self.auth._get_token()
        request.headers["Authorization"] = f"Bearer {self.auth.token}"

    def open(self, *args, **kwargs) -> Client:  # type: ignore # pylint: disable=arguments-differ
        return super().open(  # type: ignore
            request_modifier=self._auth_modifier,
            *args,
            **kwargs,
        )