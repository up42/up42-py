import datetime
import enum
from typing import List, Optional, Union
from urllib import parse

from up42 import asset, asset_searcher
from up42 import auth as up42_auth
from up42 import host, order, utils

logger = utils.get_logger(__name__)


class AllowedStatuses(enum.Enum):
    CREATED = "CREATED"
    BEING_PLACED = "BEING_PLACED"
    PLACED = "PLACED"
    PLACEMENT_FAILED = "PLACEMENT_FAILED"
    DELIVERY_INITIALIZATION_FAILED = "DELIVERY_INITIALIZATION_FAILED"
    BEING_FULFILLED = "BEING_FULFILLED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    DOWNLOADED = "DOWNLOADED"
    FULFILLED = "FULFILLED"
    FAILED_PERMANENTLY = "FAILED_PERMANENTLY"


class Storage:
    """
    The Storage class enables access to the UP42 storage. You can list
    your assets and orders within an UP42 workspace.

    Use the storage:
    ```python
    storage = up42.initialize_storage()
    ```
    """

    def __init__(self, auth: up42_auth.Auth, workspace_id: str):
        self.auth = auth
        self.workspace_id = workspace_id

    def __repr__(self):
        return f"Storage(workspace_id: {self.workspace_id})"

    @property
    def pystac_client(self):
        return utils.stac_client(self.auth.client.auth)

    def get_assets(
        self,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        workspace_id: Optional[str] = None,
        collection_names: Optional[List[str]] = None,
        producer_names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
        return_json: bool = False,
    ) -> Union[List[asset.Asset], List[dict]]:
        """
        Gets a list of assets in storage as [Asset](https://sdk.up42.com/structure/#asset) objects or in JSON format.

        Args:
            created_after: Search for assets created after the specified timestamp, in `"YYYY-MM-DD"` format.
            created_before: Search for assets created before the specified timestamp, in `"YYYY-MM-DD"` format.
            workspace_id: Search by the workspace ID.
            collection_names: Search for assets from any of the provided geospatial collections.
            producer_names: Search for assets from any of the provided producers.
            tags: Search for assets with any of the provided tags.
            sources: Search for assets from any of the provided sources.\
                The allowed values: `"ARCHIVE"`, `"TASKING"`, `"USER"`.
            search: Search for assets that contain the provided search query in their name, title, or order ID.
            limit: The number of results on a results page.
            sortby: The property to sort by.
            descending: The sorting order: <ul><li>`true` — descending</li><li>`false` — ascending</li></ul>
            return_json: If `true`, returns a JSON dictionary.\
                If `false`, returns a list of [Asset](https://sdk.up42.com/structure/#functionality_1) objects.

        Returns:
            A list of Asset objects.
        """
        params: asset_searcher.AssetSearchParams = {
            "createdAfter": created_after and utils.format_time(created_after),
            "createdBefore": created_before and utils.format_time(created_before),
            "workspaceId": workspace_id,
            "collectionNames": collection_names,
            "producerNames": producer_names,
            "tags": tags,
            "sources": sources,
            "search": search,
        }
        assets_json = asset_searcher.search_assets(
            self.auth,
            params=params,
            limit=limit,
            sortby=sortby,
            descending=descending,
        )

        if return_json:
            return assets_json
        else:
            return [asset.Asset(asset_info=asset_json) for asset_json in assets_json]

    def get_orders(
        self,
        workspace_orders: bool = True,
        return_json: bool = False,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
        order_type: Optional[str] = None,
        statuses: Optional[List[AllowedStatuses]] = None,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[List[order.Order], List[dict]]:
        """
        Gets all orders in the account/workspace as Order objects or JSON.

        Args:
            workspace_orders: If set to True, only returns workspace orders. Otherwise, returns all account orders.
            return_json: If set to True, returns JSON object.
            limit: Optional, only return n first assets by sorting criteria and order.
                Optimal to select if your workspace contains many assets.
            sortby: The sorting criteria, one of "createdAt", "updatedAt", "status", "dataProvider", "type".
            descending: The sorting order, True for descending (default), False for ascending.
            order_type: Can be either "TASKING" or "ARCHIVE". Pass this param to filter orders based on order_type.
            statuses: Search for orders with any of the statuses provided.
            name: Search for orders that contain this string in their name.
            tags: Search for orders with any of the provided tags.

        Returns:
            Order objects in the workspace or alternatively JSON info of the orders.
        """
        allowed_statuses = {entry.value for entry in AllowedStatuses}

        allowed_sorting_criteria = {
            "createdAt",
            "updatedAt",
            "type",
            "status",
        }
        if sortby not in allowed_sorting_criteria:
            raise ValueError(f"sortby parameter must be one of {allowed_sorting_criteria}!")
        sort = f"""{sortby},{"desc" if descending else "asc"}"""
        base_url = host.endpoint("/v2/orders")

        params = {
            "sort": sort,
            "workspaceId": self.workspace_id if workspace_orders else None,
            "displayName": name,
            "type": order_type if order_type in ["TASKING", "ARCHIVE"] else None,
            "tags": tags,
            "status": set(statuses) & allowed_statuses if statuses else None,
        }
        params = {k: v for k, v in params.items() if v is not None}
        url = parse.urljoin(base_url, "?" + parse.urlencode(params, doseq=True, safe=""))

        orders_json = asset_searcher.query_paginated_endpoints(auth=self.auth, url=url, limit=limit)
        logger_message = f"Got {len(orders_json)} orders" + (
            f" for workspace {self.workspace_id}." if workspace_orders else ""
        )
        logger.info(logger_message)

        if return_json:
            return orders_json
        else:
            return [order.Order(order_id=order_json["id"], order_info=order_json) for order_json in orders_json]
