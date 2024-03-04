import datetime as dt
from dataclasses import dataclass

import requests
from requests import auth

from up42.http import config, http_adapter


@dataclass(eq=True, frozen=True)
class Token:
    access_token: str
    expires_on: dt.datetime

    @property
    def has_expired(self):
        return self.expires_on <= dt.datetime.now()


class ProjectAuth(requests.auth.AuthBase):
    def __init__(
        self,
        supply_credentials_settings=config.ProjectCredentialsSettings,
        supply_token_settings=config.TokenProviderSettings,
        create_adapter=http_adapter.create,
    ):
        credentials_settings = supply_credentials_settings()
        token_settings = supply_token_settings()
        self.client_id = credentials_settings.client_id
        self.client_secret = credentials_settings.client_secret
        self.token_url = token_settings.token_url
        self.duration = token_settings.duration
        self.timeout = token_settings.timeout
        self.adapter = create_adapter(include_post=True)
        self._token = self._fetch_token()

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.token.access_token}"
        return request

    def _fetch_token(self):
        basic_auth = auth.HTTPBasicAuth(self.client_id, self.client_secret)
        session = requests.Session()
        session.mount("https://", self.adapter)
        auth_response = session.post(
            url=self.token_url,
            auth=basic_auth,
            data={"grant_type": "client_credentials"},
            timeout=self.timeout,
        )
        access_token = auth_response.json()["access_token"]
        expires_on = dt.datetime.now() + dt.timedelta(seconds=self.duration)
        return Token(access_token=access_token, expires_on=expires_on)

    @property
    def token(self):
        if self._token.has_expired:
            self._token = self._fetch_token()
        return self._token
