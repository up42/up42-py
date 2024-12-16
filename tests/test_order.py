from typing import Optional

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import asset, order

ASSET_ORDER_ID = "22d0b8e9-b649-4971-8adc-1a5eac1fa6f3"
ORDER_URL = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
ORDER_PLACEMENT_URL = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"


class TestOrder:
    aoi = {"some": "aoi"}
    image_id = "some-image-id"
    acquisition_start = "some-acquisition-start"
    acquisition_end = "some-acquisition-end"
    geometry = {"some": "geometry"}
    extra_description = "extra-description"
    sub_status: order.TaskingOrderSubStatus = "FEASIBILITY_WAITING_UPLOAD"

    @pytest.mark.parametrize(
        "order_type, details, expected_details",
        [
            ("ARCHIVE", {}, None),
            (
                "ARCHIVE",
                {"orderDetails": {"aoi": aoi, "imageId": image_id}},
                order.ArchiveOrderDetails(aoi=aoi, image_id=image_id),
            ),
            ("TASKING", {}, None),
            (
                "TASKING",
                {
                    "orderDetails": {
                        "acquisitionStart": acquisition_start,
                        "acquisitionEnd": acquisition_end,
                        "geometry": geometry,
                        "extraDescription": extra_description,
                        "subStatus": sub_status,
                    }
                },
                order.TaskingOrderDetails(
                    acquisition_start=acquisition_start,
                    acquisition_end=acquisition_end,
                    geometry=geometry,
                    extra_description=extra_description,
                    sub_status=sub_status,
                ),
            ),
        ],
    )
    def test_should_get_tasking_order(
        self,
        requests_mock: req_mock.Mocker,
        order_type: order.OrderType,
        details: dict,
        expected_details: Optional[order.OrderDetails],
    ):
        display_name = "display-name"
        status: order.OrderStatus = "CREATED"
        account_id = "some-account-id"
        data_product_id = "some-data-product-id"
        tags = ["some", "tags"]
        info = {
            "id": constants.ORDER_ID,
            "displayName": display_name,
            "workspaceId": constants.WORKSPACE_ID,
            "accountId": account_id,
            "status": status,
            "type": order_type,
            "dataProductId": data_product_id,
            "tags": tags,
        } | details
        requests_mock.get(url=ORDER_URL, json=info)
        order_obj = order.Order(
            id=constants.ORDER_ID,
            display_name=display_name,
            workspace_id=constants.WORKSPACE_ID,
            account_id=account_id,
            status=status,
            type=order_type,
            data_product_id=data_product_id,
            tags=tags,
            details=expected_details,
        )
        assert order.Order.get(constants.ORDER_ID) == order_obj

    @pytest.fixture(scope="class", params=["catalog", "tasking"])
    def order_parameters(self, request) -> order.OrderParams:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("FULFILLED", True),
            ("OTHER STATUS", False),
        ],
        ids=["FULFILLED", "OTHER STATUS"],
    )
    def test_should_compute_is_fulfilled(
        self,
        requests_mock: req_mock.Mocker,
        status: str,
        expected: bool,
        order_metadata: dict,
    ):
        requests_mock.get(url=ORDER_URL, json=order_metadata | {"status": status})
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        assert order_obj.is_fulfilled == expected

    @pytest.mark.parametrize(
        "status",
        [
            "FULFILLED",
            "BEING_FULFILLED",
        ],
    )
    def test_should_get_assets_if_valid(self, requests_mock: req_mock.Mocker, status: str, order_metadata: dict):
        requests_mock.get(url=ORDER_URL, json=order_metadata | {"status": status})
        url_asset_info = f"{constants.API_HOST}/v2/assets?search={constants.ORDER_ID}"
        asset_info = {
            "content": [
                {
                    "id": ASSET_ORDER_ID,
                }
            ],
            "totalPages": 1,
        }
        requests_mock.get(url=url_asset_info, json=asset_info)
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        (asset_obj,) = order_obj.get_assets()
        assert isinstance(asset_obj, asset.Asset)
        assert asset_obj.asset_id == ASSET_ORDER_ID

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
    def test_fails_to_get_assets_if_not_fulfilled(
        self, requests_mock: req_mock.Mocker, status: str, order_metadata: dict
    ):
        requests_mock.get(url=ORDER_URL, json=order_metadata | {"status": status})
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        with pytest.raises(order.UnfulfilledOrder, match=f".*{constants.ORDER_ID}.*{status}"):
            order_obj.get_assets()

    def test_should_track_order_status_until_fulfilled(self, requests_mock: req_mock.Mocker, order_metadata: dict):
        statuses = ["PLACED", "BEING_FULFILLED", "FULFILLED"]
        responses = [{"json": order_metadata | {"status": status}} for status in statuses]
        requests_mock.get(ORDER_URL, responses)
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        assert order_obj.track_status(report_time=0.1) == "FULFILLED"

    @pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
    def test_fails_to_track_order_if_status_not_valid(
        self, requests_mock: req_mock.Mocker, status: str, order_metadata: dict
    ):
        requests_mock.get(
            url=ORDER_URL,
            json=order_metadata | {"status": status},
        )
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        with pytest.raises(order.FailedOrder):
            order_obj.track_status()

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

    @pytest.mark.parametrize(
        "order_metadata, data_order",
        [("ARCHIVE", "ARCHIVE"), ("TASKING", "TASKING")],
        indirect=True,
    )
    def test_should_place_order(
        self,
        requests_mock: req_mock.Mocker,
        order_parameters: order.OrderParams,
        order_metadata: dict,
        data_order: order.Order,
    ):
        requests_mock.post(
            url=ORDER_PLACEMENT_URL,
            json={"results": [order_metadata], "errors": []},
        )
        assert order.Order.place(order_parameters, constants.WORKSPACE_ID) == data_order

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
