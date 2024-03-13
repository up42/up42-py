import datetime as dt
from dataclasses import dataclass
from typing import Optional, Protocol
from warnings import warn

import requests
from requests import auth

from up42.http import config, http_adapter


@dataclass(eq=True, frozen=True)
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
    def __init__(self, settings: config.ProjectCredentialsSettings):
        self.client_id = settings.project_id
        self.client_secret = settings.project_api_key

    def __call__(self, session: requests.Session, token_url: str, timeout: int) -> str:
        basic_auth = auth.HTTPBasicAuth(self.client_id, self.client_secret)
        return session.post(
            url=token_url,
            auth=basic_auth,
            data={"grant_type": "client_credentials"},
            timeout=timeout,
        ).json()["access_token"]


class AccountTokenRetriever:
    def __init__(self, settings: config.AccountCredentialsSettings):
        self.username = settings.username
        self.password = settings.password

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
        settings=config.TokenProviderSettings(),
        create_adapter=http_adapter.create,
    ):
        self.token_url = settings.token_url
        self.duration = settings.duration
        self.timeout = settings.timeout
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


def detect_settings(credentials: dict) -> Optional[config.CredentialsSettings]:
    if all(credentials.values()):
        keys = credentials.keys()
        if keys == {"project_id", "project_api_key"}:
            warn(
                "Project based authentication will be deprecated."
                "Please follow authentication guidelines (/docs/authentication.md)."
            )
            return config.ProjectCredentialsSettings(**credentials)
        if keys == {"username", "password"}:
            return config.AccountCredentialsSettings(**credentials)
        raise InvalidCredentials(f"Credentials {credentials} are not supported")
    elif any(credentials.values()):
        raise IncompleteCredentials(f"Credentials {credentials} are incomplete")
    return None


def detect_retriever(settings: config.CredentialsSettings):
    if isinstance(settings, config.ProjectCredentialsSettings):
        return ProjectTokenRetriever(settings)
    if isinstance(settings, config.AccountCredentialsSettings):
        return AccountTokenRetriever(settings)
    raise UnsupportedSettings(f"Settings {settings} are not supported")


class InvalidCredentials(ValueError):
    pass


class IncompleteCredentials(ValueError):
    pass


class UnsupportedSettings(ValueError):
    pass
