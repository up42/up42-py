import logging

from up42 import asset, catalog, main, order, storage, tasking, utils, webhooks

logger = utils.get_logger(__name__, level=logging.INFO)

DEPRECATION_MESSAGE = "after May 15th, 2024, and will be replaced by new processing functionalities."
INITIALIZED_MSG = "Initialized %s"


@main.check_auth
def initialize_catalog() -> catalog.Catalog:
    """
    Returns a Catalog object for using the catalog search.
    """
    return catalog.Catalog(auth=main.get_auth_safely())


@main.check_auth
def initialize_tasking() -> "tasking.Tasking":
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return tasking.Tasking(auth=main.get_auth_safely())


@main.check_auth
def initialize_storage() -> storage.Storage:
    """
    Returns a Storage object to list orders and assets.
    """
    return storage.Storage(auth=main.get_auth_safely())


@main.check_auth
def initialize_order(order_id: str) -> order.Order:
    """
    Returns an Order object (has to exist on UP42).
    Args:
        order_id: The UP42 order_id
    """
    up42_order = order.Order(auth=main.get_auth_safely(), order_id=order_id)
    logger.info(INITIALIZED_MSG, up42_order)
    return up42_order


@main.check_auth
def initialize_asset(asset_id: str) -> asset.Asset:
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    up42_asset = asset.Asset(auth=main.get_auth_safely(), asset_id=asset_id)
    logger.info(INITIALIZED_MSG, up42_asset)
    return up42_asset


@main.check_auth
def initialize_webhook(webhook_id: str) -> webhooks.Webhook:
    """
    Returns a Webhook object (has to exist on UP42).
    Args:
        webhook_id: The UP42 webhook_id
    """
    webhook = webhooks.Webhook(auth=main.get_auth_safely(), webhook_id=webhook_id)
    logger.info(INITIALIZED_MSG, webhook)
    return webhook
