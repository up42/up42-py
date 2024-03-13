import functools
import pathlib
from typing import Optional, Union

from up42 import utils
from up42.http import config, oauth


class Client:
    def __init__(self, retrieve: oauth.TokenRetriever, create_auth):
        self.auth = create_auth(retrieve)

    @property
    def token(self):
        return self.auth.token.access_token


Settings = Union[config.AccountCredentialsSettings, config.ProjectCredentialsSettings]


def _merge(left: Optional[Settings], right: Optional[Settings]):
    if all([left, right]):
        raise MultipleCredentialsSources("Multiple sources of credentials provided")
    return left or right


def merge_settings(
    cfg_file: Union[str, pathlib.Path, None],
    project_id: Optional[str],
    project_api_key: Optional[str],
    username: Optional[str],
    password: Optional[str],
    read_config=utils.read_json,
    detect_settings=oauth.detect_settings,
):
    possible_settings = [
        detect_settings(settings)
        for settings in [
            read_config(cfg_file) or {},
            {"project_id": project_id, "project_api_key": project_api_key},
            {"username": username, "password": password},
        ]
    ]
    result = functools.reduce(_merge, possible_settings)
    if result:
        return result
    raise MissingCredentials


def create(
    cfg_file: Union[str, pathlib.Path, None],
    project_id: Optional[str],
    project_api_key: Optional[str],
    username: Optional[str],
    password: Optional[str],
    get_settings=merge_settings,
    detect_retriever=oauth.detect_retriever,
    create_auth=oauth.Up42Auth,
):
    settings = get_settings(cfg_file, project_id, project_api_key, username, password)
    return Client(detect_retriever(settings), create_auth)


class MissingCredentials(ValueError):
    pass


class MultipleCredentialsSources(ValueError):
    pass
