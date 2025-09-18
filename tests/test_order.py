import dataclasses
import urllib
import uuid
from typing import Any, List, Optional
from unittest import mock

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import order, utils

ACCOUNT_ID = str(uuid.uuid4())
ORDER_URL = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
ORDER_PLACEMENT_URL = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
ORDER_INFO = {
    "id": constants.ORDER_ID,
    "status": "CREATED",
    "other": "data",
    "createdAt": "2023-01-01T12:00:00Z",
    "updatedAt": "2023-01-01T12:30:00Z",
}


@pytest.fixture(name="base_order_metadata")
def _base_order_metadata():
    return {
        "id": constants.ORDER_ID,
        "workspaceId": constants.WORKSPACE_ID,
        "accountId": ACCOUNT_ID,
        "displayName": "base-order",
        "status": "CREATED",
        "type": "ARCHIVE",
        "dataProductId": constants.DATA_PRODUCT_ID,
        "tags": ["some", "tags"],
    }


@pytest.fixture(name="archive_order_metadata")
def _archive_order_metadata(base_order_metadata: dict):
    return base_order_metadata | {
        "displayName": "archive-order",
        "orderDetails": {"aoi": {"some": "aoi"}, "imageId": "image-id"},
    }


@pytest.fixture(name="tasking_order_metadata")
def _tasking_order_metadata(base_order_metadata: dict):
    return base_order_metadata | {
        "displayName": "tasking-order",
        "type": "TASKING",
        "orderDetails": {
            "acquisitionStart": "acquisition-start",
            "acquisitionEnd": "acquisition-end",
            "geometry": {"some": "geometry"},
            "extraDescription": "extra-description",
            "subStatus": "FEASIBILITY_WAITING_UPLOAD",
            "acquisitionMode": "mono",
            "maxCloudCover": 10,
            "maxIncidenceAngle": 10,
            "geometricProcessing": "orthorectified",
            "projection": "4326",
            "pixelCoding": "16bit",
            "radiometricProcessing": "reflectance",
            "spectralBands": "pansharpened_3_band_true_color",
            "priority": "standard",
            "minBH": 10,
            "maxBH": 10,
            "resolution": "0.50",
            "polarization": "hh",
            "sceneSize": "20x10",
            "looks": "2",
        },
    }


@pytest.fixture(params=["BASE", "ARCHIVE", "TASKING"], name="order_metadata")
def _order_metadata(
    base_order_metadata,
    archive_order_metadata: dict,
    tasking_order_metadata: dict,
    request,
):
    return {
        "BASE": base_order_metadata,
        "ARCHIVE": archive_order_metadata,
        "TASKING": tasking_order_metadata,
    }[request.param]


@pytest.fixture(name="base_order")
def _base_order(base_order_metadata: dict):
    return order.Order(
        id=constants.ORDER_ID,
        workspace_id=constants.WORKSPACE_ID,
        account_id=ACCOUNT_ID,
        display_name="base-order",
        status="CREATED",
        type="ARCHIVE",
        data_product_id=constants.DATA_PRODUCT_ID,
        tags=["some", "tags"],
        info=base_order_metadata,
        details=None,
    )


@pytest.fixture(name="archive_order")
def _archive_order(base_order: order.Order, archive_order_metadata: dict):
    details = archive_order_metadata["orderDetails"]
    return dataclasses.replace(
        base_order,
        display_name="archive-order",
        details=order.ArchiveOrderDetails(aoi=details["aoi"], image_id=details["imageId"]),
        info=archive_order_metadata,
    )


@pytest.fixture(name="tasking_order")
def _tasking_order(base_order: order.Order, tasking_order_metadata: dict):
    return dataclasses.replace(
        base_order,
        display_name="tasking-order",
        type="TASKING",
        details=order.TaskingOrderDetails(
            acquisition_start="acquisition-start",
            acquisition_end="acquisition-end",
            geometry={"some": "geometry"},
            extra_description="extra-description",
            sub_status="FEASIBILITY_WAITING_UPLOAD",
            acquisition_mode="mono",
            max_cloud_cover=10,
            max_incidence_angle=10,
            geometric_processing="orthorectified",
            projection="4326",
            pixel_coding="16bit",
            radiometric_processing="reflectance",
            spectral_bands="pansharpened_3_band_true_color",
            priority="standard",
            min_bh=10,
            max_bh=10,
            resolution="0.50",
            polarization="hh",
            scene_size="20x10",
            looks="2",
        ),
        info=tasking_order_metadata,
    )


parameterize_with_order_data = pytest.mark.parametrize(
    "data_order, order_metadata",
    [("BASE", "BASE"), ("ARCHIVE", "ARCHIVE"), ("TASKING", "TASKING")],
    indirect=True,
)


@pytest.fixture(params=["BASE", "ARCHIVE", "TASKING"], name="data_order")
def _data_order(
    base_order: order.Order,
    archive_order: order.Order,
    tasking_order: order.Order,
    request,
):
    return {"BASE": base_order, "ARCHIVE": archive_order, "TASKING": tasking_order}[request.param]


class TestOrder:
    @pytest.fixture(scope="class", params=["catalog", "tasking"])
    def order_parameters(self, request) -> order.OrderParams:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    def test_should_provide_order_id(self, data_order: order.Order):
        assert data_order.order_id == constants.ORDER_ID

    @parameterize_with_order_data
    def test_should_provide_order_details(self, data_order: order.Order, order_metadata: dict):
        assert data_order.order_details == order_metadata.get("orderDetails", {})

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("FULFILLED", True),
            ("OTHER STATUS", False),
        ],
    )
    def test_should_compute_is_fulfilled(self, data_order: order.Order, status: order.OrderStatus, expected: bool):
        assert dataclasses.replace(data_order, status=status).is_fulfilled == expected

    @pytest.mark.parametrize(
        "status",
        [
            "FULFILLED",
            "BEING_FULFILLED",
        ],
    )
    def test_should_get_assets_if_valid(
        self,
        status: order.OrderStatus,
        data_order: order.Order,
    ):
        with mock.patch("up42.asset.Asset.all") as get_assets:
            get_assets.return_value = iter([mock.sentinel])
            assert dataclasses.replace(data_order, status=status).get_assets() == [mock.sentinel]
            get_assets.assert_called_with(search=constants.ORDER_ID)

    @pytest.mark.parametrize(
        "status",
        [
            "CREATED",
            "BEING_PLACED",
            "PLACED",
            "PLACEMENT_FAILED",
            "DELIVERY_INITIALIZATION_FAILED",
            "DOWNLOAD_FAILED",
            "DOWNLOADED",
            "FAILED_PERMANENTLY",
        ],
    )
    def test_fails_to_get_assets_if_not_fulfilled(self, status: order.OrderStatus, data_order: order.Order):
        with pytest.raises(order.UnfulfilledOrder, match=f".*{constants.ORDER_ID}.*{status}"):
            dataclasses.replace(data_order, status=status).get_assets()

    @parameterize_with_order_data
    def test_should_track_order_status_until_fulfilled(
        self,
        requests_mock: req_mock.Mocker,
        data_order: order.Order,
        order_metadata: dict,
    ):
        statuses = ["PLACED", "BEING_FULFILLED", "FULFILLED"]
        responses = [{"json": order_metadata | {"status": status}} for status in statuses]
        requests_mock.get(ORDER_URL, responses)
        assert data_order.track_status(report_time=0.1) == "FULFILLED"

    @pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
    @parameterize_with_order_data
    def test_fails_to_track_order_if_status_not_valid(
        self,
        requests_mock: req_mock.Mocker,
        status: str,
        data_order: order.Order,
        order_metadata: dict,
    ):
        requests_mock.get(
            url=ORDER_URL,
            json=order_metadata | {"status": status},
        )
        with pytest.raises(order.FailedOrder):
            data_order.track_status()

    @parameterize_with_order_data
    def test_should_get(
        self,
        requests_mock: req_mock.Mocker,
        data_order: order.Order,
        order_metadata: dict,
    ):
        requests_mock.get(url=ORDER_URL, json=order_metadata)
        assert order.Order.get(constants.ORDER_ID) == data_order

    def test_should_estimate(self, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams):
        order_estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
        expected_credits = 100
        requests_mock.post(
            url=order_estimate_url,
            json={
                "summary": {"totalCredits": expected_credits},
                "errors": [],
            },
        )
        assert order.Order.estimate(order_parameters) == expected_credits

    @parameterize_with_order_data
    def test_should_place_order(
        self,
        requests_mock: req_mock.Mocker,
        order_parameters: order.OrderParams,
        data_order: order.Order,
        order_metadata: dict,
    ):
        requests_mock.post(
            url=ORDER_PLACEMENT_URL,
            json={"results": [{"id": constants.ORDER_ID}], "errors": []},
        )
        requests_mock.get(
            url=ORDER_URL,
            json=order_metadata,
        )
        assert order.Order.place(order_parameters, constants.WORKSPACE_ID) == data_order

    def test_should_not_represent_order_info(
        self,
        data_order: order.Order,
    ):
        assert "info" not in repr(data_order)

    def test_fails_to_place_order_if_response_contains_error(
        self, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams
    ):
        error_msg = "test error"
        order_response_with_error = {"results": [], "errors": [{"message": error_msg}]}
        requests_mock.post(
            url=ORDER_PLACEMENT_URL,
            json=order_response_with_error,
        )
        with pytest.raises(order.FailedOrderPlacement, match=error_msg):
            order.Order.place(order_parameters, constants.WORKSPACE_ID)

    @pytest.mark.parametrize("workspace_id", [None, constants.WORKSPACE_ID])
    @pytest.mark.parametrize("order_type", [None, "ARCHIVE", "TASKING"])
    @pytest.mark.parametrize("status", [None, ["CREATED", "PLACED"]])
    @pytest.mark.parametrize("sub_status", [None, ["FEASIBILITY_WAITING_UPLOAD", "QUOTATION_WAITING_UPLOAD"]])
    @pytest.mark.parametrize("display_name", [None, "display-name"])
    @pytest.mark.parametrize("tags", [None, ["some", "tags"]])
    @pytest.mark.parametrize("sort_by", [None, order.OrderSorting.created_at])
    @parameterize_with_order_data
    def test_should_get_all(
        self,
        workspace_id: Optional[str],
        order_type: Optional[order.OrderType],
        status: Optional[List[order.OrderStatus]],
        sub_status: Optional[List[order.OrderSubStatus]],
        display_name: Optional[str],
        tags: Optional[List[str]],
        sort_by: Optional[utils.SortingField],
        requests_mock: req_mock.Mocker,
        data_order: order.Order,
        order_metadata: dict,
    ):
        query_params: dict[str, Any] = {}
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if order_type:
            query_params["type"] = order_type
        if status:
            query_params["status"] = status
        if sub_status:
            query_params["subStatus"] = sub_status
        if display_name:
            query_params["displayName"] = display_name
        if tags:
            query_params["tags"] = tags
        if sort_by:
            query_params["sort"] = str(sort_by)

        base_url = f"{constants.API_HOST}/v2/orders"
        expected = [order_metadata] * 4
        for page in [0, 1]:
            query_params["page"] = page
            query = urllib.parse.urlencode(query_params, doseq=True, safe="")
            url = base_url + (query and f"?{query}")
            offset = page * 2
            response = {
                "content": expected[offset : offset + 2],  # noqa: E203
                "totalPages": 2,
            }
            requests_mock.get(url=url, json=response)

        orders = order.Order.all(
            workspace_id=workspace_id,
            order_type=order_type,
            status=status,
            sub_status=sub_status,
            display_name=display_name,
            tags=tags,
            sort_by=sort_by,
        )
        orders_list = list(orders)
        assert orders_list == [data_order] * 4

        for order_item in orders_list:
            if order_item.type == "TASKING":
                assert hasattr(order_item.details, "acquisition_mode")
                assert hasattr(order_item.details, "max_cloud_cover")
                assert hasattr(order_item.details, "max_incidence_angle")
                assert hasattr(order_item.details, "geometric_processing")
                assert hasattr(order_item.details, "projection")
                assert hasattr(order_item.details, "pixel_coding")
                assert hasattr(order_item.details, "radiometric_processing")
                assert hasattr(order_item.details, "spectral_bands")
                assert hasattr(order_item.details, "priority")
                assert hasattr(order_item.details, "min_bh")
                assert hasattr(order_item.details, "max_bh")
                assert hasattr(order_item.details, "resolution")
                assert hasattr(order_item.details, "polarization")
                assert hasattr(order_item.details, "scene_size")
                assert hasattr(order_item.details, "looks")
