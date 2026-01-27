import dataclasses
import urllib
import uuid
from typing import Any

import pytest
import requests_mock as req_mock

from tests import constants, helpers
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
    def order_parameters(self, request) -> order.OrderParamsV2:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    def test_should_provide_order_id(self, data_order: order.Order):
        assert data_order.id == constants.ORDER_ID

    @parameterize_with_order_data
    def test_should_provide_order_details(
        self,
        data_order: order.Order,
        order_metadata: dict,
    ):
        raw_details = order_metadata.get("orderDetails", {})
        if not raw_details:
            assert data_order.details is None
            return

        assert data_order.details is not None

        if order_metadata["type"] == "TASKING":
            assert isinstance(data_order.details, order.TaskingOrderDetails)
        elif order_metadata["type"] == "ARCHIVE":
            assert isinstance(data_order.details, order.ArchiveOrderDetails)

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("FULFILLED", True),
            ("OTHER STATUS", False),
        ],
    )
    def test_should_compute_is_fulfilled(self, data_order: order.Order, status: order.OrderStatus, expected: bool):
        assert dataclasses.replace(data_order, status=status).is_fulfilled == expected

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
        # The IDE/linter will not issue a warning because you are explicitly
        # storing the result, even if you don't use it.
        _ = data_order.track(report_time=0.1) == "FULFILLED"
        assert data_order.status == "FULFILLED"

    @pytest.mark.parametrize("status", ["FAILED_PERMANENTLY"])
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
            data_order.track()

    @pytest.mark.parametrize("status", ["CANCELED"])
    @parameterize_with_order_data
    def test_fails_to_track_order_if_status_canceled(
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
        with pytest.raises(order.CanceledOrder):
            data_order.track()

    @parameterize_with_order_data
    def test_should_get(
        self,
        requests_mock: req_mock.Mocker,
        data_order: order.Order,
        order_metadata: dict,
    ):
        requests_mock.get(url=ORDER_URL, json=order_metadata)
        assert order.Order.get(constants.ORDER_ID) == data_order

    def test_should_not_represent_order_info(
        self,
        data_order: order.Order,
    ):
        assert "info" not in repr(data_order)

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
        workspace_id: str | None,
        order_type: order.OrderType | None,
        status: list[order.OrderStatus] | None,
        sub_status: list[order.OrderSubStatus] | None,
        display_name: str | None,
        tags: list[str] | None,
        sort_by: utils.SortingField | None,
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

    @parameterize_with_order_data
    def test_should_update(
        self,
        requests_mock: req_mock.Mocker,
        data_order: order.Order,
        order_metadata: dict,
    ):
        new_tag = ["new_tag"]
        updated_metadata = order_metadata.copy()
        updated_metadata["tags"] = new_tag
        requests_mock.patch(
            url=ORDER_URL, additional_matcher=helpers.match_request_body({"tags": new_tag}), json=updated_metadata
        )
        expected_order = dataclasses.replace(data_order, tags=new_tag, info=updated_metadata)
        assert order.Order.update(constants.ORDER_ID, new_tag) == expected_order

    def test_update_without_tags_makes_no_changes(
        self, requests_mock: req_mock.Mocker, base_order_metadata: dict, base_order: order.Order
    ):
        requests_mock.patch(url=ORDER_URL, additional_matcher=helpers.match_request_body({}), json=base_order_metadata)
        assert order.Order.update(constants.ORDER_ID) == base_order

    def test_update_with_empty_tags_removes_existing(
        self, requests_mock: req_mock.Mocker, base_order_metadata: dict, base_order: order.Order
    ):
        updated_metadata = base_order_metadata.copy()
        updated_metadata["tags"] = []
        requests_mock.patch(
            url=ORDER_URL, additional_matcher=helpers.match_request_body({"tags": []}), json=updated_metadata
        )
        expected_order = dataclasses.replace(base_order, tags=[], info=updated_metadata)
        assert order.Order.update(constants.ORDER_ID, []) == expected_order

    def test_update_handles_error_response(self, requests_mock: req_mock.Mocker):
        requests_mock.patch(url=ORDER_URL, status_code=500, json={"error": "Internal Server Error"})
        with pytest.raises(Exception):
            order.Order.update(constants.ORDER_ID, ["fail"])

    def test_update_handles_malformed_response(self, requests_mock: req_mock.Mocker):
        requests_mock.patch(url=ORDER_URL, json={"unexpected": "data"})
        with pytest.raises(KeyError):
            order.Order.update(constants.ORDER_ID, ["bad"])

    @pytest.mark.parametrize(
        "status, can_cancel",
        [
            ("CREATED", True),
            ("PLACEMENT_FAILED", True),
            ("FULFILLED", False),
            ("PLACED", False),
            ("FAILED_PERMANENTLY", False),
        ],
    )
    def test_cancel_behavior(
        self, requests_mock: req_mock.Mocker, data_order: order.Order, status: order.OrderStatus, can_cancel: bool
    ):
        data_order = dataclasses.replace(data_order, status=status)

        if can_cancel:
            cancel_response = {"orderId": data_order.id, "status": "CANCELED"}
            requests_mock.post(
                url=f"{constants.API_HOST}/v2/orders/{data_order.id}/cancellation",
                json=cancel_response,
            )

            result = data_order.cancel()
            assert isinstance(result, order.CancelOrder)
            assert result.order_id == data_order.id
            assert result.status == "CANCELED"
        else:
            with pytest.raises(order.OrderCannotBeCanceled) as exc_info:
                data_order.cancel()
            assert f"Order with id {data_order.id} cannot be canceled" in str(exc_info.value)
