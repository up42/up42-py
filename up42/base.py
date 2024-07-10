import logging
import pathlib
import warnings
from typing import Any, Optional, Union

import pystac_client
import requests

from up42 import auth as up42_auth
from up42 import host, utils

logger = utils.get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)


class UserNotAuthenticated(ValueError):
    pass


def _authenticated(value: Any):
    if value:
        return value
    raise UserNotAuthenticated("User not authenticated.")


class _Workspace:
    _auth: Optional[up42_auth.Auth] = None
    _id: Optional[str] = None

    @property
    def auth(self):
        return _authenticated(self._auth)

    @property
    def id(self):
        return _authenticated(self._id)

    def authenticate(
        self,
        cfg_file: Optional[Union[str, pathlib.Path]] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Authenticate with UP42, either using account credentials or a config JSON file
        containing the corresponding credentials.

        Args:
            cfg_file: File path to the cfg.json with {username: "...", password: "..."}.
            username: The username for the UP42 account (email UP42 console).
            password: Password for the UP42 console login.
        """
        self._auth = up42_auth.Auth(
            cfg_file=cfg_file,
            username=username,
            password=password,
        )
        url = host.endpoint("/users/me")
        self._id = self.auth.session.get(url).json()["data"]["id"]

    def get_credits_balance(self) -> dict:
        """
        Display the overall credits available in your account.

        Returns:
            A dict with the balance of credits available in your account.
        """
        endpoint_url = host.endpoint("/accounts/me/credits/balance")
        return self.auth.session.get(url=endpoint_url).json()["data"]


workspace = _Workspace()

authenticate = workspace.authenticate
get_credits_balance = workspace.get_credits_balance


class Session:
    def __get__(self, obj, obj_type=None) -> requests.Session:
        return workspace.auth.session


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
        return utils.stac_client(workspace.auth.client.auth)
