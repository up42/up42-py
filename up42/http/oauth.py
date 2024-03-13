import dataclasses as dc
import datetime as dt
from typing import Protocol

import requests
from requests import auth

from up42.http import config, http_adapter


@dc.dataclass(eq=True, frozen=True)
class Token:
    access_token: str
    expires_on: dt.datetime

    @property
    def has_expired(self) -> bool:
        return self.expires_on <= dt.datetime.now()


class TokenRetriever(Protocol):
    def __call__(self, session: requests.Session, token_url: str, timeout: int) -> str:
        ...


class ProjectTokenRetriever:
    def __init__(self, supply_credentials_settings=config.ProjectCredentialsSettings):
        credentials_settings = supply_credentials_settings()
        self.client_id = credentials_settings.client_id
        self.client_secret = credentials_settings.client_secret

    def __call__(self, session: requests.Session, token_url: str, timeout: int) -> str:
        basic_auth = auth.HTTPBasicAuth(self.client_id, self.client_secret)
        return session.post(
            url=token_url,
            auth=basic_auth,
            data={"grant_type": "client_credentials"},
            timeout=timeout,
        ).json()["access_token"]


class AccountTokenRetriever:
    def __init__(self, supply_credentials_settings=config.AccountCredentialsSettings):
        credentials_settings = supply_credentials_settings()
        self.username = credentials_settings.username
        self.password = credentials_settings.password

    def __call__(self, session: requests.Session, token_url: str, timeout: int) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        return session.post(
            url=token_url,
            data=body,
            headers=headers,
            timeout=timeout,
        ).json()["access_token"]


class Up42Auth(requests.auth.AuthBase):
    def __init__(
        self,
        retrieve: TokenRetriever,
        supply_token_settings=config.TokenProviderSettings,
        create_adapter=http_adapter.create,
    ):
        token_settings = supply_token_settings()
        self.token_url = token_settings.token_url
        self.duration = token_settings.duration
        self.timeout = token_settings.timeout
        self.adapter = create_adapter(include_post=True)
        self.retrieve = retrieve
        self._token = self._fetch_token()

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = f"Bearer {self.token.access_token}"
        return request

    def _fetch_token(self):
        session = requests.Session()
        session.mount("https://", self.adapter)
        access_token = self.retrieve(session, self.token_url, self.timeout)
        expires_on = dt.datetime.now() + dt.timedelta(seconds=self.duration)
        return Token(access_token=access_token, expires_on=expires_on)

    @property
    def token(self) -> Token:
        if self._token.has_expired:
            self._token = self._fetch_token()
        return self._token
