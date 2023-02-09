__all__ = [
    "authenticate",
    "get_webhooks",
    "create_webhook",
    "get_webhook_events",
    "get_blocks",
    "get_block_details",
    "get_block_coverage",
    "get_credits_balance",
    "get_credits_history",
    "validate_manifest",
]

import warnings
from pathlib import Path
from typing import Union, List, Optional, Dict
import logging
from datetime import datetime, date, timedelta
import json
from functools import wraps

import requests.exceptions
import pandas as pd


# pylint: disable=wrong-import-position
from up42.auth import Auth
from up42.webhooks import Webhooks, Webhook
from up42.utils import get_logger, format_time

logger = get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)


# pylint: disable=global-statement
_auth: Auth = None  # type: ignore


def authenticate(
    cfg_file: Union[str, Path] = None,
    project_id: Optional[str] = None,
    project_api_key: Optional[str] = None,
    **kwargs,
):
    """
    Authenticate with UP42, either via project_id & project_api_key, or a config json file containing both.
    Also see the documentation https://sdk.up42.com/authentication/

    Args:
        cfg_file: A json file containing project_id & project_api_key
        project_id: The UP42 project id.
        project_api_key: The UP42 project api key.

    Examples:
        ```python
        up42.authenticate(
            project_id="your-project-ID",
            project_api_key="your-project-API-key"
        )
        ```
    """
    global _auth
    _auth = Auth(
        cfg_file=cfg_file,
        project_id=project_id,
        project_api_key=project_api_key,
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
        return_json: If true returns the webhooks information as json instead of webhook class objects.
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
    webhook = Webhooks(auth=_auth).create_webhook(
        name=name, url=url, events=events, active=active, secret=secret
    )
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
        as_dataframe: Returns a dataframe instead of json (default).

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
        blocks_json = [
            block for block in public_blocks_json if block["type"] == "PROCESSING"
        ]
    else:
        blocks_json = public_blocks_json

    if basic:
        logger.info(
            "Getting blocks name and id, use basic=False for all block details."
        )
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
        as_dataframe: Returns a dataframe instead of json (default).

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
def get_credits_history(
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
) -> Dict[str, Union[str, int, Dict]]:
    """
    Display the overall credits history consumed in your account.
    The consumption history will be returned for all workspace_ids on your account.

    Args:
        start_date: The start date for the credit consumption search, datetime or isoformat string e.g.
            2021-12-01. Default start_date None uses 2000-01-01.
        end_date: The end date for the credit consumption search, datetime or isoformat string e.g.
            2021-12-31. Default end_date None uses current date.

    Returns:
        A dict with the information of the credit consumption records for all the users linked by the account_id.
        (see https://docs.up42.com/developers/api#operation/getHistory for output description)
    """
    if start_date is None:
        start_date = "2000-01-01"
    if end_date is None:
        tomorrow_date = date.today() + timedelta(days=1)
        tomorrow_datetime = datetime(
            year=tomorrow_date.year,
            month=tomorrow_date.month,
            day=tomorrow_date.day,
        )
        end_date = tomorrow_datetime.strftime("%Y-%m-%d")

    search_parameters = dict(
        {
            "from": format_time(start_date),
            "to": format_time(end_date, set_end_of_day=True),
            "size": 2000,  # 2000 is the maximum page size for this call
            "page": 0,
        }
    )
    endpoint_url = f"{_auth._endpoint()}/accounts/me/credits/history"
    response_json: dict = _auth._request(
        request_type="GET", url=endpoint_url, querystring=search_parameters
    )
    isLastPage = response_json["data"]["last"]
    credit_history = response_json["data"]["content"].copy()
    result = dict(response_json["data"])
    del result["content"]
    while not isLastPage:
        search_parameters["page"] += 1
        response_json = _auth._request(
            request_type="GET", url=endpoint_url, querystring=search_parameters
        )
        isLastPage = response_json["data"]["last"]
        credit_history.extend(response_json["data"]["content"].copy())
    result["content"] = credit_history
    return result


@_check_auth
def validate_manifest(path_or_json: Union[str, Path, dict]) -> dict:
    """
    Validates a block manifest json.

    The block manifest is required to build a custom block on UP42 and contains
    the metadata about the block as well as block input and output capabilities.
    Also see the
    [manifest chapter in the UP42 documentation](https://docs.up42.com/reference/block-manifest.html).

    Args:
        path_or_json: The input manifest, either a filepath or json string, see example.

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
