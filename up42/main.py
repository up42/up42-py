import logging
import pathlib
import warnings
from typing import Any, List, Optional, Union

from up42 import auth as up42_auth
from up42 import host, utils, webhooks

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
        resp = self.auth.request("GET", url)
        self._id = resp["data"]["id"]


workspace = _Workspace()

authenticate = workspace.authenticate


def get_webhooks(return_json: bool = False) -> List[webhooks.Webhook]:
    """
    Gets all registered webhooks for this workspace.

    Args:
        return_json: If true returns the webhooks information as JSON instead of webhook class objects.
    Returns:
        A list of the registered webhooks for this workspace.
    """
    return webhooks.Webhooks(auth=workspace.auth).get_webhooks(return_json=return_json)


def create_webhook(
    name: str,
    url: str,
    events: List[str],
    active: bool = False,
    secret: Optional[str] = None,
):
    """
    Registers a new webhook in the system.

    Args:
        name: Webhook name
        url: Unique URL where the webhook will send the message (HTTPS required)
        events: List of event types (order status / job task status)
        active: Webhook status.
        secret: String that acts as signature to the https request sent to the url.
    Returns:
        A dict with details of the registered webhook.
    """
    return webhooks.Webhooks(auth=workspace.auth).create_webhook(
        name=name, url=url, events=events, active=active, secret=secret
    )


def get_webhook_events() -> dict:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    return webhooks.Webhooks(auth=workspace.auth).get_webhook_events()


def get_credits_balance() -> dict:
    """
    Display the overall credits available in your account.

    Returns:
        A dict with the balance of credits available in your account.
    """
    endpoint_url = host.endpoint("/accounts/me/credits/balance")
    response_json = workspace.auth.request(request_type="GET", url=endpoint_url)
    return response_json["data"]
