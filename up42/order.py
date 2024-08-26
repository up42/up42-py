import copy
import time
from typing import Any, Dict, Iterator, List, Literal, Optional, TypedDict

from up42 import asset
from up42 import auth as up42_auth
from up42 import base, host, utils

logger = utils.get_logger(__name__)

MAX_ITEM = 200
LIMIT = 200


def _translate_construct_parameters(order_parameters):
    order_parameters_v2 = copy.deepcopy(order_parameters)
    params = order_parameters_v2["params"]
    data_product_id = order_parameters_v2["dataProduct"]
    default_name = f"{data_product_id} order"
    order_parameters_v2["displayName"] = params.get("displayName", default_name)
    aoi = params.pop("aoi", None) or params.pop("geometry", None)
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": aoi,
            }
        ],
    }
    order_parameters_v2["featureCollection"] = feature_collection
    return order_parameters_v2


OrderStatus = Literal[
    "CREATED",
    "BEING_PLACED",
    "PLACED",
    "BEING_FULFILLED",
    "DELIVERY_INITIALIZATION_FAILED",
    "DOWNLOAD_FAILED",
    "DOWNLOADED",
    "FULFILLED",
    "FAILED",
    "FAILED_PERMANENTLY",
]

OrderSubtatus = Literal[
    "FEASIBILITY_WAITING_UPLOAD",
    "FEASIBILITY_WAITING_RESPONSE",
    "QUOTATION_WAITING_UPLOAD",
    "QUOTATION_WAITING_RESPONSE",
    "QUOTATION_ACCEPTED",
]


class OrderParams(TypedDict):
    """
    Represents the stucture data format for the order parameters.
    dataProduct: The dataProduct id for the specific product configuration.
    params: Order parameters for each product. \
        They are different from product to product depending on product schema.
    tags: User tags to helping to identify the order.
    """

    dataProduct: str  # pylint: disable=invalid-name
    params: Dict[str, Any]
    tags: List[str]


class Order:
    """
    The Order class enables you to place, inspect and get information on orders.

    Use an existing order:
    ```python
    order = up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")
    ```
    """

    session = base.Session()
    workspace_id = base.WorkspaceId()

    def __init__(
        self,
        order_id: str,
        order_parameters: Optional[dict] = None,
        order_info: Optional[dict] = None,
    ):
        self.order_id = order_id
        self.order_parameters = order_parameters
        if order_info is not None:
            self._info = order_info
        else:
            self._info = self.info

    def __repr__(self):
        return (
            f"""Order(order_id: {self.order_id}, status: {self._info["status"]},"""
            f"""createdAt: {self._info["createdAt"]}, updatedAt: {self._info["updatedAt"]})"""
        )

    def __eq__(self, other: Optional[object]):
        return other and hasattr(other, "_info") and other._info == self._info

    @property
    def info(self) -> dict:
        """
        Gets and updates the order information.
        """
        url = host.endpoint(f"/v2/orders/{self.order_id}")
        self._info = self.session.get(url=url).json()
        return self._info

    @property
    def status(self) -> OrderStatus:
        """
        Gets the Order status. One of `PLACED`, `FAILED`, `FULFILLED`, `BEING_FULFILLED`, `FAILED_PERMANENTLY`.
        """
        status = self.info["status"]
        logger.info("Order is %s", status)
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

    def get_assets(self) -> Iterator[asset.Asset]:
        """
        Gets the Order assets or results.
        """

        def get_pages(endpoint: str, params: dict[str, Any]):
            response = self.session.get(host.endpoint(endpoint), params=params).json()
            total_pages = response["totalPages"]
            while True:
                yield response["content"]
                params["page"] += 1
                if params["page"] == total_pages:
                    break
                response = self.session.get(host.endpoint(endpoint), params=params).json()

        if not (self.is_fulfilled) and self.status != "BEING_FULFILLED":
            raise ValueError(f"Order {self.order_id} is not valid. Current status is {self.status}")
        params = {"search": self.order_id, "page": 0}
        for page in get_pages("/v2/assets", params):
            for asset_info in page:
                yield asset.Asset(base.workspace.auth, asset_info=asset_info)

    @classmethod
    def place(cls, order_parameters: dict, workspace_id: str) -> "Order":
        """
        Places an order.

        Args:
            auth: An authentication object.
            order_parameters: A dictionary for the order configuration.

        Returns:
            Order: The placed order.
        """
        url = host.endpoint(f"/v2/orders?workspaceId={workspace_id}")
        response_json = cls.session.post(url=url, json=_translate_construct_parameters(order_parameters)).json()
        if response_json["errors"]:
            message = response_json["errors"][0]["message"]
            raise ValueError(f"Order was not placed: {message}")
        order_id = response_json["results"][0]["id"]
        order_obj = Order(order_id=order_id, order_parameters=order_parameters)
        logger.info("Order %s is now %s.", order_obj.order_id, order_obj.status)
        return order_obj

    @staticmethod
    def estimate(auth: up42_auth.Auth, order_parameters: OrderParams) -> int:
        """
        Returns an estimation of the cost of an order.

        Args:
            auth: An authentication object.
            order_parameters: A dictionary for the order configuration.

        Returns:
            int: The estimated cost of the order
        """

        url = host.endpoint("/v2/orders/estimate")
        response_json = auth.request(
            request_type="POST",
            url=url,
            data=_translate_construct_parameters(order_parameters),
        )
        estimated_credits: int = response_json["summary"]["totalCredits"]
        logger.info(
            "Order is estimated to cost %s UP42 credits (order_parameters: %s)",
            estimated_credits,
            order_parameters,
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

        logger.info("Tracking order status, reporting every %s seconds...", report_time)
        time_asleep = 0

        # check order details and react for tasking orders.

        while not self.is_fulfilled:
            status = self.status
            substatus_message = (
                substatus_messages(self.order_details.get("subStatus", "")) if self.info["type"] == "TASKING" else ""
            )
            if status in ["PLACED", "BEING_FULFILLED"]:
                if time_asleep != 0 and time_asleep % report_time == 0:
                    logger.info("Order is %s! - %s", status, self.order_id)
                    logger.info(substatus_message)

            elif status in ["FAILED", "FAILED_PERMANENTLY"]:
                logger.info("Order is %s! - %s", status, self.order_id)
                raise ValueError("Order has failed!")

            time.sleep(report_time)
            time_asleep += report_time

        logger.info("Order is fulfilled successfully! - %s", self.order_id)
        return self.status
