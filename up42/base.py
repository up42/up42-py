import logging
import pathlib
import warnings
from typing import Any, Literal, Optional, Union

import pystac_client
import requests

from up42 import host, utils
from up42.http import client, oauth

logger = utils.get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)


class UserNotAuthenticated(ValueError):
    pass


def _authenticated(value: Any):
    if value:
        return value
    raise UserNotAuthenticated("User not authenticated.")


class _Workspace:
    _id: Optional[str] = None
    _session: Optional[requests.Session] = None
    _auth: Optional[oauth.Up42Auth] = None

    @property
    def id(self):
        return _authenticated(self._id)

    @property
    def session(self):
        return _authenticated(self._session)

    @property
    def auth(self):
        return _authenticated(self._auth)

    def authenticate(
        self,
        cfg_file: Optional[Union[str, pathlib.Path]] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        region: Literal["eu", "sa"] = "eu",
    ):
        """
        Authenticate with UP42, either using account credentials or a config JSON file
        containing the corresponding credentials.

        Args:
            cfg_file: File path to the cfg.json with {username: "...", password: "..."}.
            username: The username for the UP42 account (email UP42 console).
            password: Password for the UP42 console login.
            region: The desired region to use for all SDK operations.
        """
        host.REGION = region
        credential_sources = client.collect_credentials(cfg_file, username, password)
        up42_client = client.create(credential_sources, host.token_endpoint())
        logger.info("Authentication with UP42 successful!")
        self._session = up42_client.session
        user_info = self.session.get(host.user_info_endpoint()).json()
        self._id = user_info["sub"]
        self._auth = up42_client.auth


workspace = _Workspace()

authenticate = workspace.authenticate


def stac_client():
    return utils.stac_client(workspace.auth)


class Session:
    def __get__(self, obj, obj_type=None) -> requests.Session:
        return workspace.session


class WorkspaceId:
    def __get__(self, obj, obj_type=None) -> str:
        if obj:
            return obj.__dict__.get("workspace_id", workspace.id)
        return workspace.id

    def __set__(self, obj, value: str) -> None:
        if value == self:
            value = workspace.id
        obj.__dict__["workspace_id"] = value


class StacClient:
    def __get__(self, obj, obj_type=None) -> pystac_client.Client:
        return stac_client()
