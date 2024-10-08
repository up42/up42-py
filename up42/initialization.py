import logging

from up42 import asset, base, catalog, order, storage, tasking, utils

logger = utils.get_logger(__name__, level=logging.INFO)

INITIALIZED_MSG = "Initialized %s"


def initialize_catalog() -> catalog.Catalog:
    """
    Returns a Catalog object for using the catalog search.
    """
    return catalog.Catalog()


def initialize_tasking() -> tasking.Tasking:
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return tasking.Tasking(auth=base.workspace.auth)


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
    up42_order = order.Order(order_id=order_id)
    logger.info(INITIALIZED_MSG, up42_order)
    return up42_order


def initialize_asset(asset_id: str) -> asset.Asset:
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    up42_asset = asset.Asset(asset_id=asset_id)
    logger.info(INITIALIZED_MSG, up42_asset)
    return up42_asset
