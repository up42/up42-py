from time import sleep
from typing import List, Optional

from up42.auth import Auth
from up42.asset import Asset
from up42.utils import (
    get_logger,
)

logger = get_logger(__name__)

DATA_PROVIDERS = ["oneatlas"]


class Order:
    """
    The Order class enables you to place, inspect and get information on orders.

    Use an existing order:
    ```python
    order = up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")
    ```
    """

    def __init__(
        self,
        auth: Auth,
        order_id: str,
        payload: Optional[dict] = None,  # dict keys dataProviderName, orderParams
        order_info: Optional[dict] = None,
    ):
        self.auth = auth
        self.workspace_id = auth.workspace_id
        self.order_id = order_id
        self.payload = payload
        if order_info is not None:
            self._info = order_info
        else:
            self._info = self.info

    def __repr__(self):
        return (
            f"Order(order_id: {self.order_id}, assets: {self._info['assets']}, "
            f"dataProvider: {self._info['dataProvider']}, status: {self._info['status']}, "
            f"createdAt: {self._info['createdAt']}, updatedAt: {self._info['updatedAt']})"
        )

    @property
    def info(self) -> dict:
        """
        Gets and updates the order information.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders/{self.order_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json["data"]
        return self._info

    @property
    def status(self) -> str:
        """
        Gets the Order status. One of `PLACED`, `FAILED`, `FULFILLED`, `BEING_FULFILLED`, `FAILED_PERMANENTLY`.
        """
        status = self.info["status"]
        logger.info(f"Order is {status}")
        return status

    @property
    def is_fulfilled(self) -> bool:
        """
        Gets `True` if the order is fulfilled, `False` otherwise.
        Also see [status attribute](order-reference.md#up42.order.Order.status).
        """
        return self.status == "FULFILLED"

    @property
    def metadata(self) -> dict:
        """
        Gets the Order metadata.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders/{self.order_id}/metadata"
        response_json = self.auth._request(request_type="GET", url=url)
        return response_json["data"]

    def get_assets(self) -> List[Asset]:
        """
        Gets the Order assets or results.
        """
        if self.is_fulfilled:
            assets: List[str] = self.info["assets"]
            return [Asset(self.auth, asset_id=asset) for asset in assets]
        raise ValueError(
            f"Order {self.order_id} is not FULFILLED! Status is {self.status}"
        )

    @classmethod
    def place(cls, auth: Auth, data_provider_name: str, order_params: dict) -> "Order":
        """
        Places an order.

        Args:
            auth: An authentication object.
            data_provider_name: The data provider name. Currently only `oneatlas` is a supported provider.
            order_params: Order definition, including `id` and `aoi`.

        Returns:
            Order: The placed order.
        """
        assert (
            data_provider_name in DATA_PROVIDERS
        ), f"Currently only {DATA_PROVIDERS} are supported as a data provider."
        order_payload = {
            "dataProviderName": data_provider_name,
            "orderParams": order_params,
        }
        url = f"{auth._endpoint()}/workspaces/{auth.workspace_id}/orders"
        response_json = auth._request(request_type="POST", url=url, data=order_payload)
        try:
            order_id = response_json["data"]["id"]  # type: ignore
        except KeyError as e:
            raise ValueError(f"Order was not placed: {response_json}") from e
        order = cls(auth=auth, order_id=order_id, payload=order_payload)
        logger.info(f"Order {order.order_id} is now {order.status}.")
        return order

    @staticmethod
    def estimate(auth: Auth, data_provider_name: str, order_params: dict) -> int:
        """
        Returns an estimation of the cost of an order.

        Args:
            auth: An authentication object.
            data_provider_name: The data provider name. Currently only `oneatlas` is a supported provider.
            order_params: Order definition, including `id` and `aoi`.

        Returns:
            int: The estimated cost of the order
        """
        assert (
            data_provider_name in DATA_PROVIDERS
        ), f"Currently only {DATA_PROVIDERS} are supported as a data provider."
        url = f"{auth._endpoint()}/workspaces/{auth.workspace_id}/orders/estimate"
        payload = {
            "dataProviderName": data_provider_name,
            "orderParams": order_params,
        }

        response_json = auth._request(request_type="POST", url=url, data=payload)
        estimated_credits: int = response_json["data"]["credits"]  # type: ignore
        logger.info(
            f"Order with order parameters {payload} is estimated to cost {estimated_credits} UP42 credits."
        )
        return estimated_credits

    def track_status(self, report_time: int = 120) -> str:
        """
        Continuously gets the order status until order is fulfilled or failed.

        Internally checks every `report_time` (s) for the status and prints the log.

        Warning:
            When placing orders of items that are in archive or cold storage,
            the order fulfillment can happen up to **24h after order placement**.
            In such cases,
            please make sure to set an appropriate `report_time`.

        Args:
            report_time: The interval (in seconds) when to get the order status.

        Returns:
            str: The final order status.
        """
        logger.info(
            f"Tracking order status, reporting every {report_time} seconds...",
        )
        time_asleep = 0

        while not self.is_fulfilled:
            status = self.status
            if status in ["PLACED", "BEING_FULFILLED"]:
                if time_asleep != 0 and time_asleep % report_time == 0:
                    logger.info(f"Order is {status}! - {self.order_id}")
            elif status in ["FAILED", "FAILED_PERMANENTLY"]:
                logger.info(f"Order is {status}! - {self.order_id}")
                raise ValueError("Order has failed!")

            sleep(report_time)
            time_asleep += report_time

        logger.info(f"Order is fulfilled successfully! - {self.order_id}")
        return self.status
