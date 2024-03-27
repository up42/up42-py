import dataclasses as dc
import datetime as dt
import warnings
from typing import Optional, Protocol

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
    def __init__(self, settings: config.ProjectCredentialsSettings):
        self.client_id = settings.project_id
        self.client_secret = settings.project_api_key

    def __call__(self, session: requests.Session, token_url: str, timeout: int) -> str:
        basic_auth = auth.HTTPBasicAuth(self.client_id, self.client_secret)
        response = session.post(
            url=token_url,
            auth=basic_auth,
            data={"grant_type": "client_credentials"},
            timeout=timeout,
        )
        if response.ok:
            return response.json()["access_token"]
        raise WrongCredentials


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
        response = session.post(
            url=token_url,
            data=body,
            headers=headers,
            timeout=timeout,
        )
        if response.ok:
            return response.json()["access_token"]
        raise WrongCredentials


class Up42Auth(requests.auth.AuthBase):
    def __init__(
        self,
        retrieve: TokenRetriever,
        token_settings: config.TokenProviderSettings,
        create_adapter=http_adapter.create,
    ):
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


def detect_settings(
    credentials: Optional[dict],
) -> Optional[config.CredentialsSettings]:
    if credentials:
        if all(credentials.values()):
            keys = credentials.keys()
            if keys == {"project_id", "project_api_key"}:
                warnings.warn(
                    "Project based authentication will be deprecated."
                    "Please follow authentication guidelines (/docs/authentication.md)."
                )
                return config.ProjectCredentialsSettings(**credentials)
            if keys == {"username", "password"}:
                return config.AccountCredentialsSettings(**credentials)
            raise InvalidCredentials
        elif any(credentials.values()):
            raise IncompleteCredentials
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


class WrongCredentials(ValueError):
    pass
