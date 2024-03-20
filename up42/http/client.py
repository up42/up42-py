import functools
from typing import Dict, List, Optional

from up42.http import config, oauth


class Client:
    def __init__(self, auth: oauth.Up42Auth):
        self.auth = auth

    @property
    def token(self):
        return self.auth.token.access_token


def _merge(left: Optional[config.CredentialsSettings], right: Optional[config.CredentialsSettings]):
    if all([left, right]):
        raise MultipleCredentialsSources("Multiple sources of credentials provided")
    return left or right


def create(
    credential_sources: List[Dict],
    token_url: str,
    detect_settings=oauth.detect_settings,
    detect_retriever=oauth.detect_retriever,
    create_auth=oauth.Up42Auth,
):
    possible_settings = [detect_settings(credentials) for credentials in credential_sources]
    settings = functools.reduce(_merge, possible_settings)
    if settings:
        token_settings = config.TokenProviderSettings(token_url=token_url)
        return Client(create_auth(detect_retriever(settings), token_settings))
    raise MissingCredentials


class MissingCredentials(ValueError):
    pass


class MultipleCredentialsSources(ValueError):
    pass
