import copy
import dataclasses
from typing import Any, Dict, List, Literal, TypedDict, cast

import tenacity as tnc

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
    info: dict

    @classmethod
    def get(cls, order_id: str) -> "Order":
        url = host.endpoint(f"/v2/orders/{order_id}")
        info = cls.session.get(url=url).json()
        return Order(info=info)

    @property
    def order_details(self) -> dict:
        return self.info.get("orderDetails", {})

    @property
    def order_id(self) -> str:
        return self.info["id"]

    @property
    def status(self) -> str:
        return self.info["status"]

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
        params: dict[str, Any] = {"search": self.order_id}

        if self.status not in ["FULFILLED", "BEING_FULFILLED"]:
            raise UnfulfilledOrder(f"""Order {self.order_id} is not valid. Current status is {self.status}""")
        return [
            asset.Asset(asset_info=asset_info) for asset_info in utils.paged_query(params, "/v2/assets", self.session)
        ]

    @classmethod
    def place(cls, order_parameters: OrderParams, workspace_id: str) -> "Order":
        url = host.endpoint(f"/v2/orders?workspaceId={workspace_id}")
        response_json = cls.session.post(url=url, json=_translate_construct_parameters(order_parameters)).json()
        if response_json["errors"]:
            message = response_json["errors"][0]["message"]
            raise FailedOrderPlacement(f"Order was not placed: {message}")
        order = cls.get(response_json["results"][0]["id"])
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

    def track(self, report_time: float = 120):
        logger.info("Tracking order updates, reporting every %s seconds...", report_time)

        @tnc.retry(
            wait=tnc.wait_fixed(report_time),
            retry=tnc.retry_if_exception_type(UnfulfilledOrder),
            reraise=True,
        )
        def update():
            order = Order.get(self.order_id)
            self.info = order.info
            sub_status = self.order_details.get("subStatus")
            sub_status_msg = f": {sub_status}" if sub_status is not None else ""

            logger.info("Order is %s! - %s", self.status + sub_status_msg, self.order_id)
            if self.status in ["FAILED", "FAILED_PERMANENTLY"]:
                raise FailedOrder("Order has failed!")
            if not self.is_fulfilled:
                raise UnfulfilledOrder

        update()

    @utils.deprecation("Order::track", "3.0.0")
    def track_status(self, report_time: float = 120) -> str:
        self.track(report_time)
        return self.status
