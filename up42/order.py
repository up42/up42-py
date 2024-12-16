import copy
import dataclasses
import time
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

from up42 import asset, base, host, utils

logger = utils.get_logger(__name__)

MAX_ITEM = 200
LIMIT = 200


class OrderParams(TypedDict, total=False):
    """
    Represents the schema for the order parameters.
    dataProduct: The dataProduct id for the specific product configuration.
    params: Order parameters for each product. \
        They are different from product to product depending on product schema.
    tags: User tags to helping to identify the order.
    """

    dataProduct: str  # pylint: disable=invalid-name
    params: Dict[str, Any]
    tags: List[str]


class OrderParamsV2(TypedDict, total=False):
    """
    Represents the schema for the order parameters for the V2 endpoint.
    dataProduct: The dataProduct id for the specific product configuration.
    displayName: The default name that will be identifying the order.
    featureCollection: The AOI of the order.
    params: Order parameters for each product.
    tags: User tags to helping to identify the order.
    """

    # pylint: disable=invalid-name
    dataProduct: str
    displayName: str
    params: Dict[str, Any]
    featureCollection: Dict[str, Any]
    tags: List[str]


def _translate_construct_parameters(order_parameters: OrderParams) -> OrderParamsV2:
    order_parameters_v2 = cast(OrderParamsV2, copy.deepcopy(order_parameters))
    params = order_parameters_v2["params"]
    data_product_id = order_parameters_v2["dataProduct"]
    order_parameters_v2["displayName"] = params.get("displayName", f"{data_product_id} order")
    aoi = params.pop("aoi", None) or params.pop("geometry", None)
    order_parameters_v2["featureCollection"] = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": aoi,
            }
        ],
    }
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


class UnfulfilledOrder(ValueError):
    pass


class FailedOrder(ValueError):
    pass


class FailedOrderPlacement(ValueError):
    pass


OrderType = Literal["TASKING", "ARCHIVE"]
TaskingOrderSubStatus = Literal[
    "FEASIBILITY_WAITING_UPLOAD",
    "FEASIBILITY_WAITING_RESPONSE",
    "QUOTATION_WAITING_UPLOAD",
    "QUOTATION_WAITING_RESPONSE",
    "QUOTATION_ACCEPTED",
    "QUOTATION_REJECTED",
]


@dataclasses.dataclass
class ArchiveOrderDetails:
    aoi: dict
    image_id: Optional[str]


@dataclasses.dataclass
class TaskingOrderDetails:
    acquisition_start: str
    acquisition_end: str
    geometry: dict
    extra_description: Optional[str]
    sub_status: Optional[TaskingOrderSubStatus]


OrderDetails = Union[ArchiveOrderDetails, TaskingOrderDetails]


@dataclasses.dataclass
class Order:
    """
    The Order class enables you to place, inspect and get information on orders.

    Use an existing order:
    ```python
    order = up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")
    ```
    """

    session = base.Session()
    id: str
    display_name: str
    status: OrderStatus
    workspace_id: str
    account_id: str
    type: OrderType
    details: Optional[OrderDetails]
    data_product_id: Optional[str]
    tags: Optional[list[str]]

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        if "orderDetails" in data:
            order_details: dict = data["orderDetails"]
            if data["type"] == "TASKING":
                details = TaskingOrderDetails(
                    acquisition_start=order_details["acquisitionStart"],
                    acquisition_end=order_details["acquisitionEnd"],
                    geometry=order_details["geometry"],
                    extra_description=order_details.get("extraDescription"),
                    sub_status=order_details.get("subStatus"),
                )
            else:
                details = ArchiveOrderDetails(aoi=order_details["aoi"], image_id=order_details.get("imageId"))
        else:
            details = None
        return Order(
            id=data["id"],
            display_name=data["displayName"],
            status=data["status"],
            workspace_id=data["workspaceId"],
            account_id=data["accountId"],
            type=data["type"],
            details=details,
            data_product_id=data.get("dataProductId"),
            tags=data.get("tags"),
        )

    @classmethod
    def get(cls, order_id: str) -> "Order":
        url = host.endpoint(f"/v2/orders/{order_id}")
        return cls.from_dict(cls.session.get(url=url).json())

    @property
    @utils.deprecation("id", "3.0.0")
    def order_id(self) -> str:
        return self.id

    @property
    @utils.deprecation("", "3.0.0")
    def info(self) -> dict:
        """
        Gets and updates the order information.
        """
        return dataclasses.asdict(self)

    @utils.deprecation("Please use order.details instead.", "3.0.0")
    @property
    def order_details(self) -> dict:
        return dataclasses.asdict(self.details)

    @property
    def is_fulfilled(self) -> bool:
        """
        Gets `True` if the order is fulfilled, `False` otherwise.
        Also see [status attribute](order-reference.md#up42.order.Order.status).
        """
        return self.status == "FULFILLED"

    def get_assets(self) -> List[asset.Asset]:
        """
        Gets the Order assets or results.
        """
        if self.status not in ["FULFILLED", "BEING_FULFILLED"]:
            raise UnfulfilledOrder(f"""Order {self.order_id} is not valid. Current status is {self.status}""")
        return [
            asset.Asset(asset_info=asset_info)
            for asset_info in utils.paged_query({"search": self.order_id}, "/v2/assets", self.session)
        ]

    @classmethod
    def place(cls, order_parameters: OrderParams, workspace_id: str) -> "Order":
        """
        Places an order.

        Args:
            order_parameters: A dictionary for the order configuration.

        Returns:
            Order: The placed order.
        """
        url = host.endpoint(f"/v2/orders?workspaceId={workspace_id}")
        response_json = cls.session.post(url=url, json=_translate_construct_parameters(order_parameters)).json()
        if response_json["errors"]:
            message = response_json["errors"][0]["message"]
            raise FailedOrderPlacement(f"Order was not placed: {message}")
        order_info = response_json["results"][0]
        order = cls.from_dict(order_info)
        logger.info("Order %s is now %s.", order.order_id, order.status)
        return order

    @classmethod
    def estimate(cls, order_parameters: OrderParams) -> int:
        """
        Returns an estimation of the cost of an order.

        Args:
            auth: An authentication object.
            order_parameters: A dictionary for the order configuration.

        Returns:
            int: The estimated cost of the order
        """

        url = host.endpoint("/v2/orders/estimate")
        response_json = cls.session.post(
            url=url,
            json=_translate_construct_parameters(order_parameters),
        ).json()
        estimated_credits: int = response_json["summary"]["totalCredits"]
        logger.info(
            "Order is estimated to cost %s UP42 credits (order_parameters: %s)",
            estimated_credits,
            order_parameters,
        )
        return estimated_credits

    def track_status(self, report_time: float = 120) -> str:
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
        logger.info("Tracking order status, reporting every %s seconds...", report_time)
        time_asleep: float = 0
        current_info = copy.deepcopy(self._info)
        while (status := current_info["status"]) != "FULFILLED":
            sub_status = current_info.get("orderDetails", {}).get("subStatus")
            status += f": {sub_status}" if sub_status is not None else ""
            if time_asleep != 0 and time_asleep % report_time == 0:
                logger.info("Order is %s! - %s", status, self.order_id)
            if status in ["FAILED", "FAILED_PERMANENTLY"]:
                raise FailedOrder("Order has failed!")
            time.sleep(report_time)
            time_asleep += report_time
            current_info = copy.deepcopy(self.info)

        logger.info("Order is fulfilled successfully! - %s", self.order_id)
        return current_info["status"]
