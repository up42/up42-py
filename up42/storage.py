from typing import Dict, List, Union

from tqdm import tqdm

from up42.auth import Auth
from up42.order import Order
from up42.asset import Asset
from up42.utils import get_logger
from up42.tools import Tools

logger = get_logger(__name__)


class Storage(Tools):
    def __init__(self, auth: Auth):
        """
        The Storage class can query all available assets within an UP42 workspace.
        """
        self.auth = auth
        self.workspace_id = auth.workspace_id

    def __repr__(self):
        env = ", env: dev" if self.auth.env == "dev" else ""
        return f"Storage(workspace_id: {self.workspace_id}{env})"

    def get_assets(self, return_json: bool = False) -> Union[List[Asset], Dict]:
        """
        Gets all assets in the workspace as Asset objects or json.

        Args:
            return_json: True returns Asset Objects.

        Returns:
            Asset objects in the workspace or alternatively json info of the assets.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/assets"
        response_json = self.auth._request(request_type="GET", url=url)
        assets_json = response_json["data"]["content"]
        logger.info(f"Got {len(assets_json)} assets for workspace {self.workspace_id}.")

        if return_json:
            return assets_json
        else:
            assets = [
                Asset(self.auth, asset_id=asset["id"]) for asset in tqdm(assets_json)
            ]
            return assets

    def get_orders(self, return_json: bool = False) -> Union[List[Order], Dict]:
        """
        Gets all orders in the workspace as Order objects or json.

        Args:
            return_json: True returns Order Objects.

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
