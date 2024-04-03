import functools
import logging
import pathlib
import warnings
from typing import Dict, List, Optional, Union

import pandas
import requests

from up42 import auth as up42_auth
from up42 import host, utils, webhooks

logger = utils.get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)

_auth: Optional[up42_auth.Auth] = None


def authenticate(
    cfg_file: Optional[Union[str, pathlib.Path]] = None,
    project_id: Optional[str] = None,
    project_api_key: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
):
    """
    Authenticate with UP42, either using project api credentials or
    account credentials or a config JSON file containing the corresponding credentials.
    Also see the documentation https://sdk.up42.com/authentication/

    Args:
        cfg_file: File path to the cfg.json with either
        {project_id: "...", project_api_key: "..."} or {username: "...", password: "..."}.
        project_id: The unique identifier of the project.
        project_api_key: The project-specific API key.
        username: The username for the UP42 account (email UP42 console).
        password: Password for the UP42 console login.
    """
    global _auth
    _auth = up42_auth.Auth(
        cfg_file=cfg_file,
        project_id=project_id,
        project_api_key=project_api_key,
        username=username,
        password=password,
    )


def get_auth_safely() -> up42_auth.Auth:
    if _auth:
        return _auth
    raise ValueError("User not authenticated.")


def check_auth(func):
    """
    Some functionality of the up42 import object can theoretically be used
    before authentication with UP42, so the auth needs to be checked first.
    """

    @functools.wraps(func)  # required for mkdocstrings
    def inner(*args, **kwargs):
        if _auth is None:
            raise RuntimeError("Not authenticated, call up42.authenticate() first")
        return func(*args, **kwargs)

    return inner


@check_auth
def get_webhooks(return_json: bool = False) -> List[webhooks.Webhook]:
    """
    Gets all registered webhooks for this workspace.

    Args:
        return_json: If true returns the webhooks information as JSON instead of webhook class objects.
    Returns:
        A list of the registered webhooks for this workspace.
    """
    return webhooks.Webhooks(auth=get_auth_safely()).get_webhooks(return_json=return_json)


@check_auth
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
    return webhooks.Webhooks(auth=get_auth_safely()).create_webhook(
        name=name, url=url, events=events, active=active, secret=secret
    )


@check_auth
def get_webhook_events() -> dict:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    return webhooks.Webhooks(auth=get_auth_safely()).get_webhook_events()


@check_auth
def get_blocks(
    block_type: Optional[str] = None,
    basic: bool = True,
    as_dataframe: bool = False,
) -> Union[List[Dict], dict, pandas.DataFrame]:
    """
    Gets a list of all public blocks on the marketplace. Can not access custom blocks.

    Args:
        block_type: Optionally filters to "data" or "processing" blocks, default None.
        basic: Optionally returns simple version {block_id : block_name}
        as_dataframe: Returns a dataframe instead of JSON (default).

    Returns:
        A list of the public blocks and their metadata. Optional a simpler version
        dict.
    """
    if block_type:
        block_type = block_type.lower()
    url = host.endpoint("/blocks")
    response_json = get_auth_safely().request(request_type="GET", url=url)
    public_blocks_json = response_json["data"]

    if block_type == "data":
        logger.info("Getting only data blocks.")
        blocks_json = [block for block in public_blocks_json if block["type"] == "DATA"]
    elif block_type == "processing":
        logger.info("Getting only processing blocks.")
        blocks_json = [block for block in public_blocks_json if block["type"] == "PROCESSING"]
    else:
        blocks_json = public_blocks_json

    if basic:
        logger.info("Getting blocks name and id, use basic=False for all block details.")
        blocks_basic = {block["name"]: block["id"] for block in blocks_json}
        if as_dataframe:
            return pandas.DataFrame.from_dict(blocks_basic, orient="index")
        else:
            return blocks_basic

    else:
        if as_dataframe:
            return pandas.DataFrame(blocks_json)
        else:
            return blocks_json


@check_auth
def get_block_details(block_id: str, as_dataframe: bool = False) -> Union[dict, pandas.DataFrame]:
    """
    Gets the detailed information about a specific public block from
    the server, includes all manifest.json and marketplace.json contents.
    Can not access custom blocks.

    Args:
        block_id: The block id.
        as_dataframe: Returns a dataframe instead of JSON (default).

    Returns:
        A dict of the block details metadata for the specific block.
    """
    url = host.endpoint(f"/blocks/{block_id}")  # public blocks
    response_json = get_auth_safely().request(request_type="GET", url=url)
    details_json = response_json["data"]

    if as_dataframe:
        return pandas.DataFrame.from_dict(details_json, orient="index").transpose()
    else:
        return details_json


@check_auth
def get_block_coverage(block_id: str) -> dict:
    """
    Gets the spatial coverage of a data/processing block as
    url or GeoJson Feature Collection.

    Args:
        block_id: The block id.

    Returns:
        A dict of the spatial coverage for the specific block.
    """
    url = host.endpoint(f"/blocks/{block_id}/coverage")
    response_json = get_auth_safely().request(request_type="GET", url=url)
    details_json = response_json["data"]
    return requests.get(details_json["url"], timeout=utils.TIMEOUT).json()


@check_auth
def get_credits_balance() -> dict:
    """
    Display the overall credits available in your account.

    Returns:
        A dict with the balance of credits available in your account.
    """
    endpoint_url = host.endpoint("/accounts/me/credits/balance")
    response_json = get_auth_safely().request(request_type="GET", url=endpoint_url)
    return response_json["data"]
