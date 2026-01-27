import functools
import pathlib
from collections.abc import Callable
from typing import TypeAlias

import requests

from up42 import utils
from up42.http import config, oauth
from up42.http import session as http_session

SessionFactory: TypeAlias = Callable[[oauth.Up42Auth], requests.Session]


class Client:
    def __init__(self, auth: oauth.Up42Auth, create_session: SessionFactory):
        self.auth = auth
        self.session = create_session(auth)


def _merge(
    left: config.CredentialsSettings | None,
    right: config.CredentialsSettings | None,
):
    if all([left, right]):
        raise MultipleCredentialsSources("Multiple sources of credentials provided")
    return left or right


SettingsDetector: TypeAlias = Callable[[dict | None], config.CredentialsSettings | None]
RetrieverDetector: TypeAlias = Callable[[config.CredentialsSettings], oauth.TokenRetriever]
AuthFactory: TypeAlias = Callable[[oauth.TokenRetriever, config.TokenProviderSettings], oauth.Up42Auth]


def create(
    credential_sources: list[dict | None],
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


ConfigurationSource: TypeAlias = str | pathlib.Path | None
ConfigurationReader: TypeAlias = Callable[[ConfigurationSource], dict | None]


def collect_credentials(
    cfg_file: ConfigurationSource,
    username: str | None,
    password: str | None,
    read_config: ConfigurationReader = utils.read_json,
) -> list[dict | None]:
    config_source = read_config(cfg_file)
    account_credentials_source = {"username": username, "password": password}
    return [config_source, account_credentials_source]


class MissingCredentials(ValueError):
    pass


class MultipleCredentialsSources(ValueError):
    pass
