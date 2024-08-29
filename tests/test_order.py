from unittest import mock

import pytest
import requests_mock as req_mock

from up42 import asset, order

from .fixtures import fixtures_globals as constants
from .fixtures import fixtures_order

ORDER_ENDPOINT_URL = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"


class TestOrder:
    def test_should_initialize_with_info_provided(self):
        auth = mock.MagicMock()
        info = {"some": "data"}
        order_obj = order.Order(auth, constants.ORDER_ID, info)
        assert order_obj.auth == auth
        assert order_obj.order_id == constants.ORDER_ID
        assert order_obj._info == info  # pylint: disable=protected-access

    def test_should_initialize(self, auth_mock, requests_mock: req_mock.Mocker):
        info = {"some": "data"}
        requests_mock.get(url=ORDER_ENDPOINT_URL, json=info)
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
        requests_mock.get(url=ORDER_ENDPOINT_URL, json=info)
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
    def test_should_provide_order_details(self, auth_mock, requests_mock: req_mock.Mocker, info: dict, expected):
        requests_mock.get(url=ORDER_ENDPOINT_URL, json=info)
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
    def test_should_compute_is_fulfilled(self, auth_mock, requests_mock: req_mock.Mocker, info: dict, expected):
        requests_mock.get(url=ORDER_ENDPOINT_URL, json=info)
        order_obj = order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)
        assert order_obj.is_fulfilled == expected

    def test_get_assets_should_search_assets_by_order_id(self, auth_mock, requests_mock):
        order_response = {"id": constants.ORDER_ID, "status": "FULFILLED"}
        requests_mock.get(url=ORDER_ENDPOINT_URL, json=order_response)
        url_asset_info = f"{constants.API_HOST}/v2/assets?search={constants.ORDER_ID}"
        requests_mock.get(url=url_asset_info, json=fixtures_order.JSON_GET_ASSETS_RESPONSE)
        order_obj = order.Order(auth=auth_mock, order_id=constants.ORDER_ID, order_info=order_response)
        (asset_returned,) = order_obj.get_assets()
        assert isinstance(asset_returned, asset.Asset)
        assert asset_returned.asset_id == constants.ASSET_ORDER_ID

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
    def test_should_fail_to_get_assets_for_unfulfilled_order(self, status):
        auth = mock.MagicMock()
        info = {"status": status}
        order_obj = order.Order(auth=auth, order_id=constants.ORDER_ID, order_info=info)
        with pytest.raises(ValueError):
            order_obj.get_assets()


def test_place_order(catalog_order_parameters, auth_mock, order_mock, requests_mock):
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": constants.ORDER_ID}],
            "errors": [],
        },
    )
    order_placed = order.Order.place(auth_mock, catalog_order_parameters, constants.WORKSPACE_ID)
    assert order_placed == order_mock
    assert order_placed.order_id == constants.ORDER_ID


def test_place_order_fails_if_response_contains_error(catalog_order_parameters, auth_mock, requests_mock):
    error_content = "test error"
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
        json={
            "results": [],
            "errors": [{"message": error_content}],
        },
    )
    with pytest.raises(ValueError) as err:
        order.Order.place(auth_mock, catalog_order_parameters, constants.WORKSPACE_ID)
    assert error_content in str(err.value)


def test_track_status_running(order_mock, requests_mock):
    del order_mock._info

    url_job_info = f"{constants.API_HOST}/v2/orders/{order_mock.order_id}"

    status_responses = [
        {
            "json": {
                "status": "PLACED",
                "type": "TASKING",
                "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
            }
        },
        {
            "json": {
                "status": "BEING_FULFILLED",
                "type": "TASKING",
                "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
            }
        },
        {
            "json": {
                "status": "FULFILLED",
                "type": "TASKING",
                "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
            }
        },
    ]
    requests_mock.get(url_job_info, status_responses)
    order_status = order_mock.track_status(report_time=0.1)
    assert order_status == "FULFILLED"


@pytest.mark.parametrize("status", ["FULFILLED"])
def test_track_status_pass(order_mock, status, requests_mock):
    del order_mock._info

    url_job_info = f"{constants.API_HOST}/v2/orders/{order_mock.order_id}"
    requests_mock.get(url=url_job_info, json={"status": status})

    order_status = order_mock.track_status()
    assert order_status == status


@pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
def test_track_status_fail(order_mock, status, requests_mock):
    del order_mock._info

    url_job_info = f"{constants.API_HOST}/v2/orders/{order_mock.order_id}"
    requests_mock.get(
        url=url_job_info,
        json={"status": status, "type": "ARCHIVE"},
    )

    with pytest.raises(ValueError):
        order_mock.track_status()


def test_estimate_order(catalog_order_parameters, auth_mock, requests_mock):
    expected_payload = {
        "summary": {"totalCredits": 100, "totalSize": 0.1, "unit": "SQ_KM"},
        "results": [{"index": 0, "credits": 100, "unit": "SQ_KM", "size": 0.1}],
        "errors": [],
    }
    url_order_estimation = f"{constants.API_HOST}/v2/orders/estimate"
    requests_mock.post(url=url_order_estimation, json=expected_payload)
    estimation = order.Order.estimate(auth_mock, catalog_order_parameters)
    assert isinstance(estimation, int)
    assert estimation == 100
