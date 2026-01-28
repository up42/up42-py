import dataclasses
from collections.abc import Iterator
from typing import Any, Literal, TypeAlias, TypedDict

import tenacity as tnc

from up42 import base, host, utils

logger = utils.get_logger(__name__)

OrderType: TypeAlias = Literal["TASKING", "ARCHIVE"]


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
    params: dict[str, Any]
    featureCollection: dict[str, Any]
    tags: list[str]


OrderStatus: TypeAlias = Literal[
    "CREATED",
    "BEING_PLACED",
    "PLACED",
    "BEING_FULFILLED",
    "FULFILLED",
    "FAILED_PERMANENTLY",
    "CANCELED",
    "PLACEMENT_FAILED",
]
OrderSubStatus: TypeAlias = Literal[
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
    image_id: str | None
    sub_status = None


@dataclasses.dataclass
class TaskingOrderDetails:
    acquisition_start: str
    acquisition_end: str
    geometry: dict
    extra_description: str | None
    sub_status: OrderSubStatus | None
    acquisition_mode: str | None = None
    max_cloud_cover: int | None = None
    max_incidence_angle: int | None = None
    geometric_processing: str | None = None
    projection: str | None = None
    pixel_coding: str | None = None
    radiometric_processing: str | None = None
    spectral_bands: str | None = None
    priority: str | None = None
    min_bh: int | None = None
    max_bh: int | None = None
    resolution: str | None = None
    polarization: str | None = None
    scene_size: str | None = None
    looks: str | None = None


OrderDetails: TypeAlias = ArchiveOrderDetails | TaskingOrderDetails


@dataclasses.dataclass
class Order:
    session = base.Session()
    id: str
    display_name: str
    status: OrderStatus
    workspace_id: str
    account_id: str
    type: OrderType
    details: OrderDetails | None
    data_product_id: str | None
    tags: list[str] | None
    info: dict = dataclasses.field(repr=False)

    @classmethod
    def get(cls, order_id: str) -> "Order":
        url = host.endpoint(f"/v2/orders/{order_id}")
        metadata = cls.session.get(url=url).json()
        return Order._from_metadata(metadata)

    @staticmethod
    def _from_metadata(data: dict) -> "Order":
        details: OrderDetails | None = None
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
        workspace_id: str | None = None,
        order_type: OrderType | None = None,
        status: list[OrderStatus] | None = None,
        sub_status: list[OrderSubStatus] | None = None,
        display_name: str | None = None,
        tags: list[str] | None = None,
        sort_by: utils.SortingField | None = None,
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

    @classmethod
    def update(
        cls,
        order_id: str,
        tags: list[str] | None = None,
    ) -> "Order":
        url = host.endpoint(f"/v2/orders/{order_id}")
        headers = {"Content-Type": "application/merge-patch+json"}

        body = {}
        if tags is not None:
            body["tags"] = tags

        metadata = cls.session.patch(url=url, json=body, headers=headers).json()
        return Order._from_metadata(metadata)

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
            if self.status in ["FAILED_PERMANENTLY"]:
                raise FailedOrder("Order has failed!")
            if self.status == "CANCELED":
                raise CanceledOrder("Order has been canceled!")
            if not self.is_fulfilled:
                raise UnfulfilledOrder

        update()
