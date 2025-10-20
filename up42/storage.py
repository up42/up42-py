import enum
import itertools
from typing import List, Literal, Optional, Union

from up42 import base, order, utils

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
