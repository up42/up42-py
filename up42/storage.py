import datetime as dt
import enum
import itertools
from typing import List, Literal, Optional, Union

from up42 import asset, base, order, utils

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


OrderSortBy = Literal["createdAt", "updatedAt", "dataProvider", "type", "status"]
OrderType = Literal["TASKING", "ARCHIVE"]


class Storage:
    """
    The Storage class enables access to the UP42 storage. You can list
    your assets and orders within an UP42 workspace.

    Use the storage:
    ```python
    storage = up42.initialize_storage()
    ```
    """

    session = base.Session()
    workspace_id = base.WorkspaceId()
    pystac_client = base.StacClient()

    @utils.deprecation("pystac::Client.search", "3.0.0")
    def get_assets(
        self,
        created_after: Optional[Union[str, dt.datetime]] = None,
        created_before: Optional[Union[str, dt.datetime]] = None,
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
        assets = list(
            itertools.islice(
                asset.Asset.all(
                    created_after=created_after,
                    created_before=created_before,
                    workspace_id=workspace_id,
                    collection_names=collection_names,
                    producer_names=producer_names,
                    tags=tags,
                    sources=sources,
                    search=search,
                    sort_by=utils.SortingField(sortby, not descending),
                ),
                limit,
            )
        )
        if return_json:
            return [a.info for a in assets]
        else:
            return assets

    @utils.deprecation("Order::all", "3.0.0")
    def get_orders(
        self,
        workspace_orders: bool = True,
        return_json: bool = False,
        limit: Optional[int] = None,
        sortby: OrderSortBy = "createdAt",
        descending: bool = True,
        order_type: Optional[OrderType] = None,
        # FIXME: should be AllowedStatuses instead of str
        statuses: Optional[List[str]] = None,
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

        orders = list(
            itertools.islice(
                order.Order.all(
                    workspace_id=self.workspace_id if workspace_orders else None,
                    display_name=name,
                    order_type=order_type,
                    tags=tags,
                    status=statuses,  # type: ignore
                    sort_by=utils.SortingField(sortby, not descending),
                ),
                limit,
            )
        )

        if return_json:
            return [o.info for o in orders]
        else:
            return orders
