import logging
from typing import List, Optional

from up42 import asset, base, catalog, order, storage, tasking, utils, webhooks

logger = utils.get_logger(__name__, level=logging.INFO)

INITIALIZED_MSG = "Initialized %s"


def initialize_catalog() -> catalog.Catalog:
    """
    Returns a Catalog object for using the catalog search.
    """
    return catalog.Catalog(auth=base.workspace.auth, workspace_id=base.workspace.id)


def initialize_tasking() -> tasking.Tasking:
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return tasking.Tasking(auth=base.workspace.auth, workspace_id=base.workspace.id)


def initialize_storage() -> storage.Storage:
    """
    Returns a Storage object to list orders and assets.
    """
    return storage.Storage(auth=base.workspace.auth, workspace_id=base.workspace.id)


def initialize_order(order_id: str) -> order.Order:
    """
    Returns an Order object (has to exist on UP42).
    Args:
        order_id: The UP42 order_id
    """
    up42_order = order.Order(auth=base.workspace.auth, order_id=order_id)
    logger.info(INITIALIZED_MSG, up42_order)
    return up42_order


def initialize_asset(asset_id: str) -> asset.Asset:
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    up42_asset = asset.Asset(auth=base.workspace.auth, asset_id=asset_id)
    logger.info(INITIALIZED_MSG, up42_asset)
    return up42_asset


@utils.deprecation("up42.Webhook::get", "2.0.0")
def initialize_webhook(webhook_id: str) -> webhooks.Webhook:
    """
    Returns a Webhook object (has to exist on UP42).
    Args:
        webhook_id: The UP42 webhook_id
    """
    webhook = webhooks.Webhook.get(webhook_id)
    logger.info(INITIALIZED_MSG, webhook)
    return webhook


@utils.deprecation("up42.Webhook::all", "2.0.0")
def get_webhooks(return_json: bool = False) -> List[webhooks.Webhook]:
    """
    Gets all registered webhooks for this workspace.

    Args:
        return_json: If true returns the webhooks information as JSON instead of webhook class objects.
    Returns:
        A list of the registered webhooks for this workspace.
    """
    return webhooks.Webhook.all(return_json=return_json)


@utils.deprecation("up42.Webhook::save", "2.0.0")
def create_webhook(
    name: str,
    url: str,
    events: List[str],
    active: bool = False,
    secret: Optional[str] = None,
) -> webhooks.Webhook:
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
    return webhooks.Webhook.create(name=name, url=url, events=events, active=active, secret=secret)


@utils.deprecation("up42.Webhook::get_webhook_events", "2.0.0")
def get_webhook_events() -> list[dict]:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    return webhooks.Webhook.get_webhook_events()
