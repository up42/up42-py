from typing import List, Union, Optional
import math

from up42.auth import Auth
from up42.order import Order
from up42.asset import Asset
from up42.utils import get_logger

logger = get_logger(__name__)


class Storage:
    """
    The Storage class enables access to the UP42 storage. You can list
    your assets and orders within an UP42 workspace.

    Use the storage:
    ```python
    storage = up42.initialize_storage()
    ```
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.workspace_id = auth.workspace_id

    def __repr__(self):
        env = ", env: dev" if self.auth.env == "dev" else ""
        return f"Storage(workspace_id: {self.workspace_id}{env})"

    def _query_paginated(
        self, url: str, limit: Optional[int] = None, size: int = 50
    ) -> List[dict]:
        """
        Helper to fetch list of items in paginated endpoint, e.g. assets, orders.

        Args:
            url (str): The base url for paginated endpoint.
            limit: Return n first elements sorted by date of creation, optional.
            size: Default number of results per pagination page. Tradeoff of number
                of results per page and API response time to query one page. Default 50.

        Returns:
            List[dict]: List of all paginated items.
        """
        url = url + f"&size={size}"

        first_page_response = self.auth._request(request_type="GET", url=url)
        num_pages = first_page_response["data"]["totalPages"]
        num_elements = first_page_response["data"]["totalElements"]
        results_list = first_page_response["data"]["content"]

        if limit is None:
            # Also covers single page (without limit)
            num_pages_to_query = num_pages
        elif limit <= size:
            return results_list[:limit]
        else:
            # Also covers single page (with limit)
            num_pages_to_query = math.ceil(min(limit, num_elements) / size)

        for page in range(1, num_pages_to_query):
            response_json = self.auth._request(
                request_type="GET", url=url + f"&page={page}"
            )
            results_list += response_json["data"]["content"]
        return results_list[:limit]

    def get_assets(
        self,
        return_json: bool = False,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> Union[List[Asset], dict]:
        """
        Gets all assets in the workspace as Asset objects or json.

        Args:
            return_json: If set to True, returns json object.
            limit: Optional, only return n first assets by sorting criteria and order.
                Optimal to select if your workspace contains many assets.
            sortby: The sorting criteria, one of "createdAt", "updatedAt", "source", "type",
                "name", "size".
            descending: The sorting order, True for descending (default), False for ascending.

        Returns:
            Asset objects in the workspace or alternatively json info of the assets.
        """
        allowed_sorting_criteria = [
            "createdAt",
            "updatedAt",
            "source",
            "type",
            "name",
            "size",
        ]
        if sortby not in allowed_sorting_criteria:
            raise ValueError(
                f"sortby parameter must be one of {allowed_sorting_criteria}!"
            )
        sort = f"{sortby},{'desc' if descending else 'asc'}"
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/assets?format=paginated&sort={sort}"
        assets_json = self._query_paginated(url=url, limit=limit)
        logger.info(f"Got {len(assets_json)} assets for workspace {self.workspace_id}.")

        if return_json:
            return assets_json  # type: ignore
        else:
            assets = [
                Asset(self.auth, asset_id=asset_json["id"], asset_info=asset_json)
                for asset_json in assets_json
            ]
            return assets

    def get_orders(
        self,
        return_json: bool = False,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> Union[List[Order], dict]:
        """
        Gets all orders in the workspace as Order objects or json.

        Args:
            return_json: If set to True, returns json object.
            limit: Optional, only return n first assets by sorting criteria and order.
                Optimal to select if your workspace contains many assets.
            sortby: The sorting criteria, one of "createdAt", "updatedAt", "status", "dataProvider".
            descending: The sorting order, True for descending (default), False for ascending.

        Returns:
            Order objects in the workspace or alternatively json info of the orders.
        """
        allowed_sorting_criteria = [
            "createdAt",
            "updatedAt",
            "type",
            "status",
            "dataProvider",
        ]
        if sortby not in allowed_sorting_criteria:
            raise ValueError(
                f"sortby parameter must be one of {allowed_sorting_criteria}!"
            )
        sort = f"{sortby},{'desc' if descending else 'asc'}"
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders?format=paginated&sort={sort}"
        orders_json = self._query_paginated(url=url, limit=limit)
        logger.info(f"Got {len(orders_json)} orders for workspace {self.workspace_id}.")

        if return_json:
            return orders_json  # type: ignore
        else:
            orders = [
                Order(self.auth, order_id=order_json["id"], order_info=order_json)
                for order_json in orders_json
            ]
            return orders
