from unittest import mock

import pytest
import requests

from up42 import asset, order

from .fixtures import fixtures_globals as constants
from .fixtures import fixtures_order


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth.session = requests.session()
        workspace_mock.id = constants.WORKSPACE_ID
        yield


def test_init(order_mock):
    assert isinstance(order_mock, order.Order)
    assert order_mock.order_id == constants.ORDER_ID


def test_order_info(order_mock):
    assert order_mock.info
    assert order_mock.info["id"] == constants.ORDER_ID


def test_repr():
    order_info = {
        "id": "your_order_id",
        "status": "PLACED",
        "createdAt": "2023-01-01T12:00:00Z",
        "updatedAt": "2023-01-01T12:30:00Z",
    }
    order_placed = order.Order(order_id="your_order_id", order_info=order_info)

    expected_repr = (
        "Order(order_id: your_order_id, status: PLACED,"
        "createdAt: 2023-01-01T12:00:00Z, updatedAt: 2023-01-01T12:30:00Z)"
    )
    assert repr(order_placed) == expected_repr


@pytest.mark.parametrize("status", ["PLACED", "FULFILLED"])
def test_order_status(order_mock, status, monkeypatch):
    monkeypatch.setattr(order.Order, "info", {"status": status})
    assert order_mock.status == status


@pytest.mark.parametrize(
    "status, order_type, order_details",
    [
        ("PLACED", "TASKING", {"subStatus": "FEASIBILITY_WAITING_UPLOAD"}),
        ("FULFILLED", "ARCHIVE", {}),
    ],
)
def test_order_details(order_mock, status, order_type, order_details, monkeypatch):
    monkeypatch.setattr(
        order.Order,
        "info",
        {"status": status, "type": order_type, "orderDetails": order_details},
    )
    assert order_mock.order_details == order_details


@pytest.mark.parametrize(
    "status,expected",
    [("NOT STARTED", False), ("PLACED", False), ("FULFILLED", True)],
)
def test_is_fulfilled(order_mock, status, expected, monkeypatch):
    monkeypatch.setattr(order.Order, "info", {"status": status})
    assert order_mock.is_fulfilled == expected


def test_order_parameters(order_mock):
    assert not order_mock.order_parameters


@pytest.mark.parametrize(
    "status",
    [
        "FULFILLED",
        "BEING_FULFILLED",
    ],
)
def test_get_assets_should_search_assets_by_order_id(requests_mock, status):
    order_response = {"id": constants.ORDER_ID, "status": status}

    url_order_info = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
    requests_mock.get(url=url_order_info, json=order_response)
    url_asset_info = f"{constants.API_HOST}/v2/assets?search={constants.ORDER_ID}&page=0"
    requests_mock.get(url=url_asset_info, json=fixtures_order.JSON_GET_ASSETS_RESPONSE)
    order_placed = order.Order(order_id=constants.ORDER_ID)
    (asset_returned,) = list(order_placed.get_assets())
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
        "DOWNLOAD_FAILED",
        "DOWNLOADED",
        "FAILED_PERMANENTLY",
    ],
)
def test_should_fail_to_get_assets_for_unfulfilled_order(requests_mock, status):
    order_response = {"id": constants.ORDER_ID, "status": status}
    url_order_info = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
    requests_mock.get(url=url_order_info, json=order_response)
    order_placed = order.Order(order_id=constants.ORDER_ID)
    with pytest.raises(ValueError):
        list(order_placed.get_assets())


def test_place_order(catalog_order_parameters, order_mock, requests_mock):
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": constants.ORDER_ID}],
            "errors": [],
        },
    )
    order_placed = order.Order.place(catalog_order_parameters, constants.WORKSPACE_ID)
    assert order_placed == order_mock
    assert order_placed.order_id == constants.ORDER_ID
    assert order_placed.order_parameters == catalog_order_parameters


def test_place_order_fails_if_response_contains_error(catalog_order_parameters, requests_mock):
    error_content = "test error"
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
        json={
            "results": [],
            "errors": [{"message": error_content}],
        },
    )
    with pytest.raises(ValueError) as err:
        order.Order.place(catalog_order_parameters, constants.WORKSPACE_ID)
    assert error_content in str(err.value)


def test_track_status_running(order_mock, requests_mock):
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
    url_job_info = f"{constants.API_HOST}/v2/orders/{order_mock.order_id}"
    requests_mock.get(url=url_job_info, json={"status": status})

    order_status = order_mock.track_status()
    assert order_status == status


@pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
def test_track_status_fail(order_mock, status, requests_mock):
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
