import logging
from typing import List, Optional, Union

from up42 import asset, catalog, main, order, storage, tasking, utils, webhooks

logger = utils.get_logger(__name__, level=logging.INFO)

INITIALIZED_MSG = "Initialized %s"


def initialize_catalog() -> catalog.Catalog:
    """
    Returns a Catalog object for using the catalog search.
    """
    return catalog.Catalog(auth=main.workspace.auth, workspace_id=main.workspace.id)


def initialize_tasking() -> "tasking.Tasking":
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return tasking.Tasking(auth=main.workspace.auth, workspace_id=main.workspace.id)


def initialize_storage() -> storage.Storage:
    """
    Returns a Storage object to list orders and assets.
    """
    return storage.Storage(auth=main.workspace.auth, workspace_id=main.workspace.id)


def initialize_order(order_id: str) -> order.Order:
    """
    Returns an Order object (has to exist on UP42).
    Args:
        order_id: The UP42 order_id
    """
    up42_order = order.Order(auth=main.workspace.auth, order_id=order_id)
    logger.info(INITIALIZED_MSG, up42_order)
    return up42_order


def initialize_asset(asset_id: str) -> asset.Asset:
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    up42_asset = asset.Asset(auth=main.workspace.auth, asset_id=asset_id)
    logger.info(INITIALIZED_MSG, up42_asset)
    return up42_asset


def initialize_webhook(webhook_id: str) -> webhooks.Webhook:
    """
    Returns a Webhook object (has to exist on UP42).
    Args:
        webhook_id: The UP42 webhook_id
    """
    webhooks.Webhook.session = main.workspace.auth.session
    webhook = webhooks.Webhook.get(webhook_id, main.workspace.id)
    logger.info(INITIALIZED_MSG, webhook)
    return webhook


def get_webhooks(
    return_json: bool = False,
) -> Union[List[webhooks.Webhook], List[dict]]:
    """
    Gets all registered webhooks for this workspace.

    Args:
        return_json: If true returns the webhooks information as JSON instead of webhook class objects.
    Returns:
        A list of the registered webhooks for this workspace.
    """
    webhooks.Webhook.session = main.workspace.auth.session
    hooks = webhooks.Webhook.all(workspace_id=main.workspace.id)
    if return_json:
        return [hook.info for hook in hooks]
    else:
        return hooks


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
    return webhooks.Webhook.create(
        name=name,
        url=url,
        events=events,
        active=active,
        secret=secret,
        workspace_id=main.workspace.id,
    )


def get_webhook_events() -> dict:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    webhooks.Webhook.session = main.workspace.auth.session
    return webhooks.Webhook.all_webhook_events()
