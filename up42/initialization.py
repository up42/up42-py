import logging

from up42 import asset, catalog, order, storage, utils

logger = utils.get_logger(__name__, level=logging.INFO)

INITIALIZED_MSG = "Initialized %s"


@utils.deprecation(None, "3.0.0")
def initialize_catalog() -> catalog.Catalog:
    """
    Returns a Catalog object for using the catalog search.
    """
    return catalog.Catalog()


@utils.deprecation(None, "3.0.0")
def initialize_storage() -> storage.Storage:
    """
    Returns a Storage object to list orders and assets.
    """
    return storage.Storage()


@utils.deprecation(None, "3.0.0")
def initialize_order(order_id: str) -> order.Order:
    """
    Returns an Order object (has to exist on UP42).
    Args:
        order_id: The UP42 order_id
    """
    up42_order = order.Order.get(order_id)
    logger.info(INITIALIZED_MSG, up42_order)
    return up42_order


@utils.deprecation(None, "3.0.0")
def initialize_asset(asset_id: str) -> asset.Asset:
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    up42_asset = asset.Asset.get(asset_id)
    logger.info(INITIALIZED_MSG, up42_asset)
    return up42_asset
