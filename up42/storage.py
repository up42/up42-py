from typing import List, Union, Optional

from tqdm import tqdm

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
        Helper to fetch list of items in paginated endpoint.

        Args:
            url (str): The base url for paginated endpoint.
            limit: Return n first elements sorted by date of creation, optional.
            size: Default number of results per pagination page. Tradeoff of number
                of results per page and API response time to query one page. Default 50.

        Returns:
            List[dict]: List of all paginated items.
        """
        if limit is None:
            url = url + f"&size={size}"
        elif limit <= size:
            url = url + f"&size={limit}"  # Most efficient page size.

        first_page_response = self.auth._request(request_type="GET", url=url)
        num_pages = first_page_response["data"]["totalPages"]
        results_list = first_page_response["data"]["content"]

        if num_pages > 1:
            for page in range(1, num_pages):
                response_json = self.auth._request(
                    request_type="GET", url=url + f"?page={page}"
                )
                results_list += response_json["data"]["content"]

        results_list = results_list[:limit]
        return results_list

    def get_assets(
        self, return_json: bool = False, limit: Optional[int] = None
    ) -> Union[List[Asset], dict]:
        """
        Gets all assets in the workspace as Asset objects or json.

        Args:
            return_json: If set to True, returns json object.
            limit: Optional, only return n first assets (sorted by date of creation).
                Optimal to select if your workspace contains many assets, which would
                slow down the query.

        Returns:
            Asset objects in the workspace or alternatively json info of the assets.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/assets?format=paginated"
        assets_json = self._query_paginated(url, limit=limit)
        logger.info(f"Got {len(assets_json)} assets for workspace {self.workspace_id}.")

        if return_json:
            return assets_json  # type: ignore
        else:
            assets = [
                Asset(self.auth, asset_id=asset["id"]) for asset in tqdm(assets_json)
            ]
            return assets

    def get_orders(
        self, return_json: bool = False, limit: Optional[int] = None
    ) -> Union[List[Order], dict]:
        """
        Gets all orders in the workspace as Order objects or json.

        Args:
            return_json: If set to True, returns json object.
            limit: Optional, only return n first orders (sorted by date of creation).
                Optimal to select if your workspace contains many orders, which would
                slow down the query.

        Returns:
            Order objects in the workspace or alternatively json info of the orders.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders?format=paginated"
        orders_json = self._query_paginated(url, limit=limit)
        logger.info(f"Got {len(orders_json)} orders for workspace {self.workspace_id}.")

        if return_json:
            return orders_json
        else:
            orders = [
                Order(self.auth, order_id=order["id"]) for order in tqdm(orders_json)
            ]
            return orders
