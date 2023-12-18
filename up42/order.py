from time import sleep
from typing import List, Optional

from up42.asset import Asset
from up42.asset_searcher import AssetSearchParams, search_assets
from up42.auth import Auth
from up42.utils import get_logger

logger = get_logger(__name__)

MAX_ITEM = 200
LIMIT = 200


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
        order_parameters: Optional[dict] = None,
        order_info: Optional[dict] = None,
    ):
        self.auth = auth
        self.order_id = order_id
        self.order_parameters = order_parameters
        if order_info is not None:
            self._info = order_info
        else:
            self._info = self.info

    def __repr__(self):
        return (
            f"Order(order_id: {self.order_id}, status: {self._info['status']},"
            f"createdAt: {self._info['createdAt']}, updatedAt: {self._info['updatedAt']})"
        )

    def __eq__(self, other: Optional[object]):
        return other and hasattr(other, "_info") and other._info == self._info

    @property
    def info(self) -> dict:
        """
        Gets and updates the order information.
        """
        url = f"{self.auth._endpoint()}/v2/orders/{self.order_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json
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
    def order_details(self) -> dict:
        """
        Gets the Order Details. Only for tasking type orders, archive types return empty.
        """
        if self.info["type"] == "TASKING":
            order_details = self.info["orderDetails"]
            return order_details
        logger.info("Order is not TASKING type. Order details are not provided.")
        return {}

    @property
    def is_fulfilled(self) -> bool:
        """
        Gets `True` if the order is fulfilled, `False` otherwise.
        Also see [status attribute](order-reference.md#up42.order.Order.status).
        """
        return self.status == "FULFILLED"

    def get_assets(self) -> List[Asset]:
        """
        Gets the Order assets or results.
        """
        if self.is_fulfilled:
            params: AssetSearchParams = {"search": self.order_id}
            assets_response = search_assets(self.auth, params=params)
            return [
                Asset(self.auth, asset_id=asset_info["id"], asset_info=asset_info) for asset_info in assets_response
            ]
        raise ValueError(f"Order {self.order_id} is not FULFILLED! Current status is {self.status}")

    @classmethod
    def place(cls, auth: Auth, order_parameters: dict) -> "Order":
        """
        Places an order.

        Args:
            auth: An authentication object.
            order_parameters: A dictionary like {dataProduct: ..., "params": {"id": ..., "aoi": ...}}

        Returns:
            Order: The placed order.
        """
        url = f"{auth._endpoint()}/workspaces/{auth.workspace_id}/orders"
        response_json = auth._request(request_type="POST", url=url, data=order_parameters)
        try:
            order_id = response_json["data"]["id"]  # type: ignore
        except KeyError as e:
            raise ValueError(f"Order was not placed: {response_json}") from e
        order = cls(auth=auth, order_id=order_id, order_parameters=order_parameters)
        logger.info(f"Order {order.order_id} is now {order.status}.")
        return order

    @staticmethod
    def estimate(auth: Auth, order_parameters: dict) -> int:
        """
        Returns an estimation of the cost of an order.

        Args:
            auth: An authentication object.
            order_parameters: A dictionary like {dataProduct: ..., "params": {"id": ..., "aoi": ...}}

        Returns:
            int: The estimated cost of the order
        """
        url = f"{auth._endpoint()}/workspaces/{auth.workspace_id}/orders/estimate"

        response_json = auth._request(request_type="POST", url=url, data=order_parameters)
        estimated_credits: int = response_json["data"]["credits"]  # type: ignore
        logger.info(
            f"Order is estimated to cost {estimated_credits} UP42 credits (order_parameters: {order_parameters})"
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

        def substatus_messages(substatus: str) -> str:
            substatus_user_messages = {
                "FEASIBILITY_WAITING_UPLOAD": "Wait for feasibility.",
                "FEASIBILITY_WAITING_RESPONSE": "Feasibility is ready.",
                "QUOTATION_WAITING_UPLOAD": "Wait for quotation.",
                "QUOTATION_WAITING_RESPONSE": "Quotation is ready",
                "QUOTATION_ACCEPTED": "In progress.",
            }

            if substatus in substatus_user_messages:
                message = substatus_user_messages[substatus]
                return f"{substatus}, {message}"
            return f"{substatus}"

        logger.info(
            f"Tracking order status, reporting every {str(report_time)} seconds...",
        )
        time_asleep = 0

        # check order details and react for tasking orders.

        while not self.is_fulfilled:
            status = self.status
            substatus_message = (
                substatus_messages(self.order_details.get("subStatus", "")) if self.info["type"] == "TASKING" else ""
            )
            if status in ["PLACED", "BEING_FULFILLED"]:
                if time_asleep != 0 and time_asleep % report_time == 0:
                    logger.info(f"Order is {status}! - {self.order_id}")
                    logger.info(substatus_message)

            elif status in ["FAILED", "FAILED_PERMANENTLY"]:
                logger.info(f"Order is {status}! - {self.order_id}")
                raise ValueError("Order has failed!")

            sleep(report_time)
            time_asleep += report_time

        logger.info(f"Order is fulfilled successfully! - {self.order_id}")
        return self.status
