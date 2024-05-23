import functools
from typing import Callable, Dict, List, Optional

import requests

from up42.http import config, oauth
from up42.http import session as http_session

SessionFactory = Callable[[oauth.Up42Auth], requests.Session]


class Client:
    def __init__(self, auth: oauth.Up42Auth, create_session: SessionFactory):
        self.auth = auth
        self.session = create_session(auth)


def _merge(
    left: Optional[config.CredentialsSettings],
    right: Optional[config.CredentialsSettings],
):
    if all([left, right]):
        raise MultipleCredentialsSources("Multiple sources of credentials provided")
    return left or right


SettingsDetector = Callable[[Optional[Dict]], Optional[config.CredentialsSettings]]
RetrieverDetector = Callable[[config.CredentialsSettings], oauth.TokenRetriever]
AuthFactory = Callable[[oauth.TokenRetriever, config.TokenProviderSettings], oauth.Up42Auth]


def create(
    credential_sources: List[Optional[Dict]],
    token_url: str,
    detect_settings: SettingsDetector = oauth.detect_settings,
    detect_retriever: RetrieverDetector = oauth.detect_retriever,
    create_auth: AuthFactory = oauth.Up42Auth,
    create_session: SessionFactory = http_session.create,
):
    possible_settings = [detect_settings(credentials) for credentials in credential_sources]
    settings = functools.reduce(_merge, possible_settings)
    if settings:
        token_settings = config.TokenProviderSettings(token_url=token_url)
        return Client(create_auth(detect_retriever(settings), token_settings), create_session)
    raise MissingCredentials


class MissingCredentials(ValueError):
    pass


class MultipleCredentialsSources(ValueError):
    pass
