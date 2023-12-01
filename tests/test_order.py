import os

import pytest

# pylint: disable=unused-import
from .context import Asset, Order
from .fixtures import (
    ASSET_ID,
    JSON_ORDER,
    ORDER_ID,
    WORKSPACE_ID,
    asset_live,
    asset_mock,
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    catalog_mock,
    order_live,
    order_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    username_test_live,
)


def test_init(order_mock):
    assert isinstance(order_mock, Order)
    assert order_mock.order_id == ORDER_ID
    assert order_mock.workspace_id == WORKSPACE_ID


def test_order_info(order_mock):
    assert order_mock.info
    assert order_mock.info["id"] == ORDER_ID


def test_repr(auth_mock):
    order_info = {
        "id": "your_order_id",
        "status": "PLACED",
        "createdAt": "2023-01-01T12:00:00Z",
        "updatedAt": "2023-01-01T12:30:00Z",
    }
    order = Order(auth_mock, order_id="your_order_id", order_info=order_info)

    expected_repr = (
        "Order(order_id: your_order_id, status: PLACED"
        "createdAt: 2023-01-01T12:00:00Z, updatedAt: 2023-01-01T12:30:00Z)"
    )
    assert repr(order) == expected_repr


@pytest.mark.live
def test_order_info_live(order_live):
    assert order_live.info
    assert order_live.info["id"] == os.getenv("TEST_UP42_ORDER_ID")
    assert order_live.info["dataProductId"] == "4f1b2f62-98df-4c74-81f4-5dce45deee99"


# pylint: disable=unused-argument
@pytest.mark.parametrize("status", ["PLACED", "FULFILLED"])
def test_order_status(order_mock, status, monkeypatch):
    monkeypatch.setattr(Order, "info", {"status": status})
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
        Order,
        "info",
        {"status": status, "type": order_type, "orderDetails": order_details},
    )
    assert order_mock.order_details == order_details


# pylint: disable=unused-argument
@pytest.mark.parametrize(
    "status,expected",
    [("NOT STARTED", False), ("PLACED", False), ("FULFILLED", True)],
)
def test_is_fulfilled(order_mock, status, expected, monkeypatch):
    monkeypatch.setattr(Order, "info", {"status": status})
    assert order_mock.is_fulfilled == expected


def test_order_parameters(order_mock):
    assert not order_mock.order_parameters


@pytest.mark.live
def test_order_parameters_live(order_live):
    assert not order_live.order_parameters


@pytest.fixture
def order_parameters():
    return {
        "dataProduct": "4f1b2f62-98df-4c74-81f4-5dce45deee99",
        "params": {
            "id": "aa1b5abf-8864-4092-9b65-35f8d0d413bb",
            "aoi": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [13.357031, 52.52361],
                        [13.350981, 52.524362],
                        [13.351544, 52.526326],
                        [13.355284, 52.526765],
                        [13.356944, 52.525067],
                        [13.357257, 52.524409],
                        [13.357031, 52.52361],
                    ]
                ],
            },
        },
        "tags": ["Test", "SDK"],
    }


def test_place_order(order_parameters, auth_mock, order_mock, requests_mock):
    requests_mock.post(
        url=f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders",
        json={
            "data": {"id": ORDER_ID},
            "error": {},
        },
    )
    order = Order.place(auth_mock, order_parameters)
    assert isinstance(order, Order)
    assert order.order_id == ORDER_ID
    assert order.order_parameters == order_parameters


def test_place_order_no_id(order_parameters, auth_mock, order_mock, requests_mock):
    requests_mock.post(
        url=f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders",
        json={
            "data": {"xyz": 892},
            "error": {},
        },
    )
    with pytest.raises(ValueError):
        Order.place(auth_mock, order_parameters)


@pytest.mark.skip(reason="Placing orders costs credits.")
@pytest.mark.live
def test_place_order_live(auth_live, order_parameters):
    order = Order.place(auth_live, order_parameters)
    assert order.status == "PLACED"
    assert order.order_parameters == order_parameters


def test_track_status_running(order_mock, requests_mock):
    del order_mock._info

    url_job_info = f"{order_mock.auth._endpoint()}/v2/orders/{order_mock.order_id}"

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

    url_job_info = f"{order_mock.auth._endpoint()}/v2/orders/{order_mock.order_id}"
    requests_mock.get(url=url_job_info, json={"status": status})

    order_status = order_mock.track_status()
    assert order_status == status


@pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
def test_track_status_fail(order_mock, status, requests_mock):
    del order_mock._info

    url_job_info = f"{order_mock.auth._endpoint()}/v2/orders/{order_mock.order_id}"
    requests_mock.get(
        url=url_job_info,
        json={"status": status, "type": "ARCHIVE"},
    )

    with pytest.raises(ValueError):
        order_mock.track_status()


def test_estimate_order(order_parameters, auth_mock, requests_mock):
    url_order_estimation = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/estimate"
    )
    requests_mock.post(url=url_order_estimation, json={"data": {"credits": 100}})
    estimation = Order.estimate(auth_mock, order_parameters)
    assert isinstance(estimation, int)
    assert estimation == 100


@pytest.mark.live
def test_estimate_order_live(order_parameters, auth_live):
    estimation = Order.estimate(auth_live, order_parameters=order_parameters)
    assert isinstance(estimation, int)
    assert estimation == 100
