from unittest import mock

import pytest
import requests_mock as req_mock

from up42 import asset, order

from .fixtures import fixtures_globals as constants

ORDER_URL = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
ORDER_PLACEMENT_URL = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"


class TestOrder:
    @pytest.fixture(scope="class", params=["catalog", "tasking"])
    def order_parameters(self, request) -> order.OrderParams:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    def test_should_initialize_with_info_provided(self):
        auth = mock.MagicMock()
        info = {"some": "data"}
        order_obj = order.Order(auth, constants.ORDER_ID, info)
        assert order_obj.auth == auth
        assert order_obj.order_id == constants.ORDER_ID
        assert order_obj._info == info  # pylint: disable=protected-access

    def test_should_initialize(self, auth_mock, requests_mock: req_mock.Mocker):
        info = {"some": "data"}
        requests_mock.get(url=ORDER_URL, json=info)
        order_obj = order.Order(auth_mock, constants.ORDER_ID)
        assert order_obj.auth == auth_mock
        assert order_obj.order_id == constants.ORDER_ID
        assert order_obj.info == info

    def test_should_provide_representation(self, auth_mock):
        info = {
            "id": constants.ORDER_ID,
            "status": "PLACED",
            "createdAt": "2023-01-01T12:00:00Z",
            "updatedAt": "2023-01-01T12:30:00Z",
        }
        order_obj = order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)
        expected_repr = (
            f"Order(order_id: {constants.ORDER_ID}, status: PLACED,"
            "createdAt: 2023-01-01T12:00:00Z, updatedAt: 2023-01-01T12:30:00Z)"
        )
        assert repr(order_obj) == expected_repr

    def test_should_provide_status(self, auth_mock, requests_mock: req_mock.Mocker):
        info = {"status": "random"}
        requests_mock.get(url=ORDER_URL, json=info)
        order_obj = order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)
        assert order_obj.status == info["status"]

    @pytest.mark.parametrize(
        "info, expected",
        [
            ({"type": "ARCHIVE"}, {}),
            (
                {"type": "TASKING", "orderDetails": {"order": "details"}},
                {"order": "details"},
            ),
        ],
        ids=["ARCHIVE", "TASKING"],
    )
    def test_should_provide_order_details(self, auth_mock, requests_mock: req_mock.Mocker, info: dict, expected: dict):
        requests_mock.get(url=ORDER_URL, json=info)
        order_obj = order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)
        assert order_obj.order_details == expected

    @pytest.mark.parametrize(
        "info, expected",
        [
            ({"status": "FULFILLED"}, True),
            ({"status": "OTHER STATUS"}, False),
        ],
        ids=["FULFILLED", "OTHER STATUS"],
    )
    def test_should_compute_is_fulfilled(self, auth_mock, requests_mock: req_mock.Mocker, info: dict, expected: bool):
        requests_mock.get(url=ORDER_URL, json=info)
        order_obj = order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)
        assert order_obj.is_fulfilled == expected

    def test_should_get_assets_if_fulfilled(self, auth_mock, requests_mock: req_mock.Mocker):
        info = {"id": constants.ORDER_ID, "status": "FULFILLED"}
        requests_mock.get(url=ORDER_URL, json=info)
        url_asset_info = f"{constants.API_HOST}/v2/assets?search={constants.ORDER_ID}"
        asset_info = {
            "content": [
                {
                    "id": constants.ASSET_ORDER_ID,
                }
            ],
            "totalPages": 1,
            "totalElements": 1,
        }
        requests_mock.get(url=url_asset_info, json=asset_info)
        order_obj = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
        (asset_obj,) = order_obj.get_assets()
        assert isinstance(asset_obj, asset.Asset)
        assert asset_obj.asset_id == constants.ASSET_ORDER_ID

    @pytest.mark.parametrize(
        "status",
        [
            "CREATED",
            "BEING_PLACED",
            "PLACED",
            "PLACEMENT_FAILED",
            "DELIVERY_INITIALIZATION_FAILED",
            "BEING_FULFILLED",
            "DOWNLOAD_FAILED",
            "DOWNLOADED",
            "FAILED_PERMANENTLY",
        ],
    )
    def test_fails_to_get_assets_if_not_fulfilled(self, auth_mock, requests_mock: req_mock.Mocker, status: str):
        info = {"status": status}
        requests_mock.get(url=ORDER_URL, json=info)
        order_obj = order.Order(auth=auth_mock, order_id=constants.ORDER_ID, order_info=info)
        with pytest.raises(order.UnfulfilledOrder, match=f".*{constants.ORDER_ID}.*{status}"):
            order_obj.get_assets()

    @pytest.mark.parametrize(
        "info",
        [{"type": "ARCHIVE"}, {"type": "TASKING", "orderDetails": {"subStatus": "substatus"}}],
        ids=["ARCHIVE", "TASKING"],
    )
    def test_should_track_order_status_until_fulfilled(self, auth_mock, requests_mock: req_mock.Mocker, info: dict):
        responses = []
        statuses = ["PLACED", "BEING_FULFILLED", "FULFILLED"]
        responses = [{"json": {"status": status, **info}} for status in statuses]
        requests_mock.get(ORDER_URL, responses)
        order_obj = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
        assert order_obj.track_status(report_time=0.1) == "FULFILLED"

    @pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
    def test_fails_to_track_order_if_status_not_valid(self, auth_mock, requests_mock: req_mock.Mocker, status: str):
        info = {"status": status, "type": "ANY"}
        requests_mock.get(
            url=ORDER_URL,
            json=info,
        )
        order_obj = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
        with pytest.raises(order.FailedOrder):
            order_obj.track_status()

    def test_should_estimate(self, auth_mock, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams):
        order_estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
        expected_credits = 100
        requests_mock.post(
            url=order_estimate_url,
            json={
                "summary": {"totalCredits": expected_credits},
                "errors": [],
            },
        )
        assert order.Order.estimate(auth_mock, order_parameters) == expected_credits

    def test_should_place_order(self, auth_mock, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams):
        info = {"status": "SOME STATUS"}
        requests_mock.get(
            url=ORDER_URL,
            json=info,
        )
        requests_mock.post(
            url=ORDER_PLACEMENT_URL,
            json={"results": [{"id": constants.ORDER_ID}], "errors": []},
        )
        order_obj = order.Order.place(auth_mock, order_parameters, constants.WORKSPACE_ID)
        assert order_obj == order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)

    def test_fails_to_place_order_if_response_contains_error(
        self, auth_mock, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams
    ):
        error_msg = "test error"
        order_response_with_error = {"results": [], "errors": [{"message": error_msg}]}
        requests_mock.post(
            url=ORDER_PLACEMENT_URL,
            json=order_response_with_error,
        )
        with pytest.raises(order.FailedOrderPlacement, match=error_msg):
            order.Order.place(auth_mock, order_parameters, constants.WORKSPACE_ID)
