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
    auth_live,
    auth_mock,
    catalog_mock,
    order_live,
    order_mock,
)


def test_init(order_mock):
    assert isinstance(order_mock, Order)
    assert order_mock.order_id == ORDER_ID
    assert order_mock.workspace_id == WORKSPACE_ID


def test_order_info(order_mock):
    assert order_mock.info
    assert order_mock.info["id"] == ORDER_ID
    assert order_mock.info["dataProvider"] == JSON_ORDER["data"]["dataProvider"]
    assert order_mock.info["assets"][0] == ASSET_ID


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


def test_get_assets(order_mock, asset_mock):
    assets = order_mock.get_assets()
    assert len(assets) == 1
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == order_mock.info["assets"][0]


def test_get_assets_placed(order_mock, asset_mock, monkeypatch):
    monkeypatch.setattr(Order, "info", {"status": "PLACED"})
    with pytest.raises(ValueError):
        order_mock.get_assets()


@pytest.mark.live
def test_get_assets_live(order_live, asset_live):
    assets = order_live.get_assets()
    assert len(assets) >= 1
    assert isinstance(assets[0], Asset)


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

    url_job_info = (
        f"{order_mock.auth._endpoint()}/workspaces/"
        f"{order_mock.workspace_id}/orders/{order_mock.order_id}"
    )

    status_responses = [
        {
            "json": {
                "data": {
                    "status": "PLACED",
                    "type": "TASKING",
                    "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
                },
                "error": {},
            }
        },
        {
            "json": {
                "data": {
                    "status": "BEING_FULFILLED",
                    "type": "TASKING",
                    "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
                },
                "error": {},
            }
        },
        {
            "json": {
                "data": {
                    "status": "FULFILLED",
                    "type": "TASKING",
                    "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
                },
                "error": {},
            }
        },
    ]
    requests_mock.get(url_job_info, status_responses)
    order_status = order_mock.track_status(report_time=0.1)
    assert order_status == "FULFILLED"


@pytest.mark.parametrize("status", ["FULFILLED"])
def test_track_status_pass(order_mock, status, requests_mock):
    del order_mock._info

    url_job_info = (
        f"{order_mock.auth._endpoint()}/workspaces/"
        f"{order_mock.workspace_id}/orders/{order_mock.order_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

    order_status = order_mock.track_status()
    assert order_status == status


@pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
def test_track_status_fail(order_mock, status, requests_mock):
    del order_mock._info

    url_job_info = (
        f"{order_mock.auth._endpoint()}/workspaces/"
        f"{order_mock.workspace_id}/orders/{order_mock.order_id}"
    )
    requests_mock.get(
        url=url_job_info,
        json={"data": {"status": status, "type": "ARCHIVE"}, "error": {}},
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
