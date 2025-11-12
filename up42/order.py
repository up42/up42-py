import dataclasses
from typing import Any, Dict, Iterator, List, Literal, Optional, TypedDict, Union

import tenacity as tnc

from up42 import base, host, utils

logger = utils.get_logger(__name__)

OrderType = Literal["TASKING", "ARCHIVE"]


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
    "CANCELED",
]
OrderSubStatus = Literal[
    "FEASIBILITY_WAITING_UPLOAD",
    "FEASIBILITY_WAITING_RESPONSE",
    "QUOTATION_WAITING_UPLOAD",
    "QUOTATION_WAITING_RESPONSE",
    "QUOTATION_ACCEPTED",
    "QUOTATION_REJECTED",
]


class UnfulfilledOrder(ValueError):
    pass


class FailedOrder(ValueError):
    pass


class CanceledOrder(ValueError):
    pass


class OrderCannotBeCanceled(ValueError):
    pass


class OrderSorting:
    created_at = utils.SortingField(name="createdAt")
    updated_at = utils.SortingField(name="updatedAt")
    type = utils.SortingField(name="type")
    status = utils.SortingField(name="status")


@dataclasses.dataclass
class CancelOrder:
    order_id: str
    status: OrderStatus


@dataclasses.dataclass
class ArchiveOrderDetails:
    aoi: dict
    image_id: Optional[str]
    sub_status = None


@dataclasses.dataclass
class TaskingOrderDetails:
    acquisition_start: str
    acquisition_end: str
    geometry: dict
    extra_description: Optional[str]
    sub_status: Optional[OrderSubStatus]
    acquisition_mode: Optional[str] = None
    max_cloud_cover: Optional[int] = None
    max_incidence_angle: Optional[int] = None
    geometric_processing: Optional[str] = None
    projection: Optional[str] = None
    pixel_coding: Optional[str] = None
    radiometric_processing: Optional[str] = None
    spectral_bands: Optional[str] = None
    priority: Optional[str] = None
    min_bh: Optional[int] = None
    max_bh: Optional[int] = None
    resolution: Optional[str] = None
    polarization: Optional[str] = None
    scene_size: Optional[str] = None
    looks: Optional[str] = None


OrderDetails = Union[ArchiveOrderDetails, TaskingOrderDetails]


@dataclasses.dataclass
class Order:
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
    info: dict = dataclasses.field(repr=False)

    @classmethod
    def get(cls, order_id: str) -> "Order":
        url = host.endpoint(f"/v2/orders/{order_id}")
        metadata = cls.session.get(url=url).json()
        return Order._from_metadata(metadata)

    @staticmethod
    def _from_metadata(data: dict) -> "Order":
        details: Optional[OrderDetails] = None
        if "orderDetails" in data:
            order_details: dict = data["orderDetails"]
            if data["type"] == "TASKING":
                details = TaskingOrderDetails(
                    acquisition_start=order_details["acquisitionStart"],
                    acquisition_end=order_details["acquisitionEnd"],
                    geometry=order_details["geometry"],
                    extra_description=order_details.get("extraDescription"),
                    sub_status=order_details.get("subStatus"),
                    acquisition_mode=order_details.get("acquisitionMode"),
                    max_cloud_cover=order_details.get("maxCloudCover"),
                    max_incidence_angle=order_details.get("maxIncidenceAngle"),
                    geometric_processing=order_details.get("geometricProcessing"),
                    projection=order_details.get("projection"),
                    pixel_coding=order_details.get("pixelCoding"),
                    radiometric_processing=order_details.get("radiometricProcessing"),
                    spectral_bands=order_details.get("spectralBands"),
                    priority=order_details.get("priority"),
                    min_bh=order_details.get("minBH"),
                    max_bh=order_details.get("maxBH"),
                    resolution=order_details.get("resolution"),
                    polarization=order_details.get("polarization"),
                    scene_size=order_details.get("sceneSize"),
                    looks=order_details.get("looks"),
                )
            else:
                details = ArchiveOrderDetails(aoi=order_details["aoi"], image_id=order_details.get("imageId"))
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
            info=data,
        )

    @classmethod
    def all(
        cls,
        workspace_id: Optional[str] = None,
        order_type: Optional[OrderType] = None,
        status: Optional[List[OrderStatus]] = None,
        sub_status: Optional[List[OrderSubStatus]] = None,
        display_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: Optional[utils.SortingField] = None,
    ) -> Iterator["Order"]:
        params = {
            "sort": sort_by,
            "workspaceId": workspace_id,
            "displayName": display_name,
            "type": order_type,
            "tags": tags,
            "status": status,
            "subStatus": sub_status,
        }
        return map(cls._from_metadata, utils.paged_query(params, "/v2/orders", cls.session))

    def cancel(self) -> CancelOrder:
        if self.status not in ["CREATED", "PLACEMENT_FAILED"]:
            raise OrderCannotBeCanceled(f"Order with id {self.id} cannot be canceled in its current status.")

        url = host.endpoint(f"/v2/orders/{self.id}/cancellation")
        metadata = self.session.post(url=url).json()
        return CancelOrder(order_id=metadata["orderId"], status=metadata["status"])

    @property
    def is_fulfilled(self) -> bool:
        """
        Gets `True` if the order is fulfilled, `False` otherwise.
        Also see [status attribute](order-reference.md#up42.order.Order.status).
        """
        return self.status == "FULFILLED"

    def track(self, report_time: float = 120):
        logger.info("Tracking order updates, reporting every %s seconds...", report_time)

        @tnc.retry(
            wait=tnc.wait_fixed(report_time),
            retry=tnc.retry_if_exception_type(UnfulfilledOrder),
            reraise=True,
        )
        def update():
            order = Order.get(self.id)
            for field in dataclasses.fields(order):
                setattr(self, field.name, getattr(order, field.name))
            sub_status = self.details and self.details.sub_status
            sub_status_msg = f": {sub_status}" if sub_status is not None else ""

            logger.info("Order is %s! - %s", self.status + sub_status_msg, self.id)
            if self.status in ["FAILED", "FAILED_PERMANENTLY"]:
                raise FailedOrder("Order has failed!")
            if self.status == "CANCELED":
                raise CanceledOrder("Order has been canceled!")
            if not self.is_fulfilled:
                raise UnfulfilledOrder

        update()
