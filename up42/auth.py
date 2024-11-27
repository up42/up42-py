"""
UP42 authentication mechanism and base requests functionality
"""

import pathlib
from typing import Callable, Dict, List, Optional, Union

import requests

from up42 import host, utils
from up42.http import client

logger = utils.get_logger(__name__)
ConfigurationSource = Optional[Union[str, pathlib.Path]]
ConfigurationReader = Callable[[ConfigurationSource], Optional[Dict]]
CredentialsMerger = Callable[
    [ConfigurationSource, Optional[str], Optional[str]],
    List[Optional[Dict]],
]
ClientFactory = Callable[[List[Optional[Dict]], str], client.Client]


def collect_credentials(
    cfg_file: ConfigurationSource,
    username: Optional[str],
    password: Optional[str],
    read_config: ConfigurationReader = utils.read_json,
) -> List[Optional[Dict]]:
    config_source = read_config(cfg_file)
    account_credentials_source = {"username": username, "password": password}
    return [config_source, account_credentials_source]


class Auth:
    def __init__(
        self,
        cfg_file: Union[str, pathlib.Path, None] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        get_credential_sources: CredentialsMerger = collect_credentials,
        create_client: ClientFactory = client.create,
    ):
        """
        The Auth class handles the authentication with UP42.

        Authenticate with UP42:
            https://sdk.up42.com/authentication/.

        Args:
            cfg_file: File path to the cfg.json with {username: "...", password: "..."}.
            username: The username for the UP42 account (email UP42 console).
            password: Password for the UP42 console login.
        """
        credential_sources = get_credential_sources(cfg_file, username, password)
        self.client = create_client(credential_sources, host.token_endpoint())
        logger.info("Authentication with UP42 successful!")

    @property
    def session(self) -> requests.Session:
        return self.client.session
