__all__ = [
    "authenticate",
    "get_webhooks",
    "create_webhook",
    "get_webhook_events",
    "get_blocks",
    "get_block_details",
    "get_block_coverage",
    "get_credits_balance",
    "validate_manifest",
]

import json
import logging
import warnings
from functools import wraps
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import requests.exceptions

# pylint: disable=wrong-import-position
from up42.auth import Auth
from up42.utils import get_logger
from up42.webhooks import Webhook, Webhooks

logger = get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)


# pylint: disable=global-statement
_auth: Auth = None  # type: ignore


def authenticate(
    cfg_file: Union[str, Path] = None,
    project_id: Optional[str] = None,
    project_api_key: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs,
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
    _auth = Auth(
        cfg_file=cfg_file,
        project_id=project_id,
        project_api_key=project_api_key,
        username=username,
        password=password,
        **kwargs,
    )


def _check_auth(func, *args, **kwargs):
    """
    Some functionality of the up42 import object can theoretically be used
    before authentication with UP42, so the auth needs to be checked first.
    """

    # pylint: disable=unused-argument
    @wraps(func)  # required for mkdocstrings
    def inner(*args, **kwargs):
        if _auth is None:
            raise RuntimeError("Not authenticated, call up42.authenticate() first")
        return func(*args, **kwargs)

    return inner


@_check_auth
def get_webhooks(return_json: bool = False) -> List[Webhook]:
    """
    Gets all registered webhooks for this workspace.

    Args:
        return_json: If true returns the webhooks information as JSON instead of webhook class objects.
    Returns:
        A list of the registered webhooks for this workspace.
    """
    webhooks = Webhooks(auth=_auth).get_webhooks(return_json=return_json)
    return webhooks


@_check_auth
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
    webhook = Webhooks(auth=_auth).create_webhook(name=name, url=url, events=events, active=active, secret=secret)
    return webhook


@_check_auth
def get_webhook_events() -> dict:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    webhook_events = Webhooks(auth=_auth).get_webhook_events()
    return webhook_events


@_check_auth
def get_blocks(
    block_type: Optional[str] = None,
    basic: bool = True,
    as_dataframe: bool = False,
) -> Union[List[Dict], dict]:
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
    try:
        block_type = block_type.lower()  # type: ignore
    except AttributeError:
        pass
    url = f"{_auth._endpoint()}/blocks"
    response_json = _auth._request(request_type="GET", url=url)
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
            return pd.DataFrame.from_dict(blocks_basic, orient="index")
        else:
            return blocks_basic

    else:
        if as_dataframe:
            return pd.DataFrame(blocks_json)
        else:
            return blocks_json


@_check_auth
def get_block_details(block_id: str, as_dataframe: bool = False) -> dict:
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
    url = f"{_auth._endpoint()}/blocks/{block_id}"  # public blocks
    response_json = _auth._request(request_type="GET", url=url)
    details_json = response_json["data"]

    if as_dataframe:
        return pd.DataFrame.from_dict(details_json, orient="index").transpose()
    else:
        return details_json


@_check_auth
def get_block_coverage(block_id: str) -> dict:
    """
    Gets the spatial coverage of a data/processing block as
    url or GeoJson Feature Collection.

    Args:
        block_id: The block id.

    Returns:
        A dict of the spatial coverage for the specific block.
    """
    url = f"{_auth._endpoint()}/blocks/{block_id}/coverage"
    response_json = _auth._request(request_type="GET", url=url)
    details_json = response_json["data"]
    response_coverage = requests.get(details_json["url"]).json()
    return response_coverage


@_check_auth
def get_credits_balance() -> dict:
    """
    Display the overall credits available in your account.

    Returns:
        A dict with the balance of credits available in your account.
    """
    endpoint_url = f"{_auth._endpoint()}/accounts/me/credits/balance"
    response_json = _auth._request(request_type="GET", url=endpoint_url)
    details_json = response_json["data"]
    return details_json


@_check_auth
def validate_manifest(path_or_json: Union[str, Path, dict]) -> dict:
    """
    Validates a block manifest JSON.

    The [block manifest](https://docs.up42.com/processing-platform/custom-blocks/manifest)
    is required to build a custom block on UP42 and contains
    the metadata about the block as well as block input and output capabilities.

    Args:
        path_or_json: The input manifest, either a filepath or JSON string, see example.

    Returns:
        A dictionary with the validation results and potential validation errors.
    """
    if isinstance(path_or_json, (str, Path)):
        with open(path_or_json) as src:
            manifest_json = json.load(src)
    else:
        manifest_json = path_or_json
    url = f"{_auth._endpoint()}/validate-schema/block"
    response_json = _auth._request(request_type="POST", url=url, data=manifest_json)
    logger.info("The manifest is valid.")
    return response_json["data"]
