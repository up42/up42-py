from typing import List, Union

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

    def _paginate(self, url: str) -> List[dict]:
        """
        Helper to fetch list of items in paginated endpoint.

        Args:
            url (str): The base paginated endpoint.

        Returns:
            List[dict]: List of all paginated items.
        """
        first_pagination_response = self.auth._request(request_type="GET", url=url)
        output = first_pagination_response["data"]["content"]
        num_pages = first_pagination_response["data"]["totalPages"]
        total_items = first_pagination_response["data"]["totalElements"]
        for page in range(1, num_pages):
            response_json = self.auth._request(
                request_type="GET", url=url + f"?page={page}"
            )
            output += response_json["data"]["content"]
        assert len(output) == total_items, "Some paginated items are missing!"
        return output

    def get_assets(self, return_json: bool = False) -> Union[List[Asset], dict]:
        """
        Gets all assets in the workspace as Asset objects or json.

        Args:
            return_json: If set to True, returns json object.

        Returns:
            Asset objects in the workspace or alternatively json info of the assets.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/assets"
        assets_json = self._paginate(url)
        logger.info(f"Got {len(assets_json)} assets for workspace {self.workspace_id}.")

        if return_json:
            return assets_json  # type: ignore
        else:
            assets = [
                Asset(self.auth, asset_id=asset["id"]) for asset in tqdm(assets_json)
            ]
            return assets

    def get_orders(self, return_json: bool = False) -> Union[List[Order], dict]:
        """
        Gets all orders in the workspace as Order objects or json.

        Args:
            return_json: If set to True, returns json object.

        Returns:
            Order objects in the workspace or alternatively json info of the orders.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders"
        response_json = self.auth._request(request_type="GET", url=url)
        orders_json = response_json["data"]["orders"]
        logger.info(f"Got {len(orders_json)} orders for workspace {self.workspace_id}.")

        if return_json:
            return orders_json
        else:
            orders = [
                Order(self.auth, order_id=order["id"]) for order in tqdm(orders_json)
            ]
            return orders
