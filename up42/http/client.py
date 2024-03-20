import functools
from typing import Callable, Dict, List, Optional

from up42.http import config, oauth

AuthFactory = Callable[[oauth.TokenRetriever], oauth.Up42Auth]


class Client:
    def __init__(self, retrieve: oauth.TokenRetriever, create_auth: AuthFactory):
        self.auth = create_auth(retrieve)

    @property
    def token(self):
        return self.auth.token.access_token


def _merge(left: Optional[config.CredentialsSettings], right: Optional[config.CredentialsSettings]):
    if all([left, right]):
        raise MultipleCredentialsSources("Multiple sources of credentials provided")
    return left or right


def create(
    credential_sources: List[Dict],
    detect_settings=oauth.detect_settings,
    detect_retriever=oauth.detect_retriever,
    create_auth=oauth.Up42Auth,
):
    possible_settings = [detect_settings(credentials) for credentials in credential_sources]
    settings = functools.reduce(_merge, possible_settings)
    if settings:
        return Client(detect_retriever(settings), create_auth)
    raise MissingCredentials


class MissingCredentials(ValueError):
    pass


class MultipleCredentialsSources(ValueError):
    pass
