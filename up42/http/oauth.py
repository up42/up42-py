import dataclasses as dc
import datetime as dt
import threading
from typing import Optional, Protocol

import requests

from up42.http import config, http_adapter

CLIENT_ID = "up42-sdk"


@dc.dataclass(eq=True, frozen=True)
class Token:
    access_token: str
    expires_on: dt.datetime

    @property
    def has_expired(self) -> bool:
        return self.expires_on <= dt.datetime.now()


class TokenRetriever(Protocol):
    def __call__(self, session: requests.Session, settings: config.TokenProviderSettings) -> Token:
        ...


class AccountTokenRetriever:
    def __init__(self, settings: config.AccountCredentialsSettings):
        self.username = settings.username
        self.password = settings.password

    def __call__(self, session: requests.Session, settings: config.TokenProviderSettings) -> Token:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": CLIENT_ID,
        }
        response = session.post(
            url=settings.token_url,
            data=body,
            headers=headers,
            timeout=settings.timeout,
        )
        if response.ok:
            token_data = response.json()
            access_token = token_data["access_token"]
            expires_on = dt.datetime.now() + dt.timedelta(seconds=token_data["expires_in"] - settings.expiry_offset)
            return Token(access_token=access_token, expires_on=expires_on)
        raise WrongCredentials


class Up42Auth(requests.auth.AuthBase):
    def __init__(
        self,
        retrieve: TokenRetriever,
        token_settings: config.TokenProviderSettings,
        create_adapter=http_adapter.create,
    ):
        self.token_settings = token_settings
        self.adapter = create_adapter(include_post=True)
        self.retrieve = retrieve
        self._token = self._fetch_token()
        self._lock = threading.Lock()

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = f"Bearer {self._access_token}"
        return request

    def _fetch_token(self):
        session = requests.Session()
        session.mount("https://", self.adapter)
        return self.retrieve(session, self.token_settings)

    @property
    def _access_token(self) -> Token:
        with self._lock:
            if self._token.has_expired:
                self._token = self._fetch_token()
        return self._token.access_token

    def __deepcopy__(self, memo: dict):
        # Pystac client deep copies the request modifier this class is used for.
        # We return the same instance to share authentication settings between
        # possible parallel calls to avoid multiple token generation.
        return self


def detect_settings(
    credentials: Optional[dict],
) -> Optional[config.CredentialsSettings]:
    if credentials:
        if all(credentials.values()):
            if credentials.keys() == {"username", "password"}:
                return config.AccountCredentialsSettings(**credentials)
            raise InvalidCredentials
        elif any(credentials.values()):
            raise IncompleteCredentials
    return None


def detect_retriever(settings: config.CredentialsSettings):
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
