import urllib
from typing import Any, List, Optional

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import asset, order, utils

ASSET_ORDER_ID = "22d0b8e9-b649-4971-8adc-1a5eac1fa6f3"
ORDER_URL = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
ORDER_PLACEMENT_URL = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
ORDER_INFO = {
    "id": constants.ORDER_ID,
    "status": "CREATED",
    "other": "data",
    "createdAt": "2023-01-01T12:00:00Z",
    "updatedAt": "2023-01-01T12:30:00Z",
}


class TestOrder:
    @pytest.fixture(scope="class", params=["catalog", "tasking"])
    def order_parameters(self, request) -> order.OrderParams:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    def test_should_provide_order_id(self):
        assert order.Order(ORDER_INFO).order_id == constants.ORDER_ID

    def test_should_provide_status(self):
        assert order.Order(ORDER_INFO).status == ORDER_INFO["status"]

    @pytest.mark.parametrize(
        "details, expected",
        [({"orderDetails": {"order": "details"}}, {"order": "details"}), ({}, {})],
    )
    def test_should_provide_order_details(self, details: dict, expected: dict):
        order_obj = order.Order(info=ORDER_INFO | details)
        assert order_obj.order_details == expected

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("FULFILLED", True),
            ("OTHER STATUS", False),
        ],
    )
    def test_should_compute_is_fulfilled(self, status: str, expected: bool):
        order_obj = order.Order(info=ORDER_INFO | {"status": status})
        assert order_obj.is_fulfilled == expected

    @pytest.mark.parametrize(
        "status",
        [
            "FULFILLED",
            "BEING_FULFILLED",
        ],
    )
    def test_should_get_assets_if_valid(self, requests_mock: req_mock.Mocker, status: str):
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
        order_obj = order.Order(info=ORDER_INFO | {"status": status})
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
    def test_fails_to_get_assets_if_not_fulfilled(self, status: str):
        order_obj = order.Order(info=ORDER_INFO | {"status": status})
        with pytest.raises(order.UnfulfilledOrder, match=f".*{constants.ORDER_ID}.*{status}"):
            order_obj.get_assets()

    @pytest.mark.parametrize(
        "extra_info",
        [
            {"type": "ARCHIVE"},
            {"type": "TASKING", "orderDetails": {"subStatus": "substatus"}},
        ],
        ids=["ARCHIVE", "TASKING"],
    )
    def test_should_track_order_status_until_fulfilled(self, requests_mock: req_mock.Mocker, extra_info: dict):
        statuses = ["PLACED", "BEING_FULFILLED", "FULFILLED"]
        responses = [{"json": ORDER_INFO | {"status": status} | extra_info} for status in statuses]
        requests_mock.get(ORDER_URL, responses)
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        assert order_obj.track_status(report_time=0.1) == "FULFILLED"

    @pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
    def test_fails_to_track_order_if_status_not_valid(self, requests_mock: req_mock.Mocker, status: str):
        requests_mock.get(
            url=ORDER_URL,
            json=ORDER_INFO | {"status": status, "type": "ANY"},
        )
        order_obj = order.Order.get(order_id=constants.ORDER_ID)
        with pytest.raises(order.FailedOrder):
            order_obj.track_status()

    def test_should_get(self, requests_mock: req_mock.Mocker):
        requests_mock.get(url=ORDER_URL, json=ORDER_INFO)
        assert order.Order.get(constants.ORDER_ID) == order.Order(ORDER_INFO)

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

    def test_should_place_order(self, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams):
        requests_mock.post(
            url=ORDER_PLACEMENT_URL,
            json={"results": [{"id": constants.ORDER_ID}], "errors": []},
        )
        requests_mock.get(
            url=ORDER_URL,
            json=ORDER_INFO,
        )
        order_obj = order.Order.place(order_parameters, constants.WORKSPACE_ID)
        assert order_obj == order.Order(info=ORDER_INFO)

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
        expected = [ORDER_INFO] * 4
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
        assert list(orders) == [order.Order(info=ORDER_INFO)] * 4
