import os

import pytest

from up42.asset import Asset
from up42.order import Order

from .fixtures.fixtures_globals import API_HOST, ASSET_ORDER_ID, ORDER_ID, WORKSPACE_ID
from .fixtures.fixtures_order import JSON_GET_ASSETS_RESPONSE


def test_init(order_mock):
    assert isinstance(order_mock, Order)
    assert order_mock.order_id == ORDER_ID


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
        "Order(order_id: your_order_id, status: PLACED,"
        "createdAt: 2023-01-01T12:00:00Z, updatedAt: 2023-01-01T12:30:00Z)"
    )
    assert repr(order) == expected_repr


@pytest.mark.live
def test_order_info_live(order_live):
    assert order_live.info
    assert order_live.info["id"] == os.getenv("TEST_UP42_ORDER_ID")
    assert (
        order_live.info["dataProductId"]
        == "4f1b2f62-98df-4c74-81f4-5dce45deee99"
    )


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
def test_order_details(
    order_mock, status, order_type, order_details, monkeypatch
):
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


def test_get_assets_should_search_assets_by_order_id(auth_mock, requests_mock):
    order_response = {"id": ORDER_ID, "status": "FULFILLED"}

    url_order_info = f"{API_HOST}/v2/orders/{ORDER_ID}"
    requests_mock.get(url=url_order_info, json=order_response)
    url_asset_info = f"{API_HOST}/v2/assets?search={ORDER_ID}&size=50"
    requests_mock.get(url=url_asset_info, json=JSON_GET_ASSETS_RESPONSE)
    order = Order(auth=auth_mock, order_id=ORDER_ID)
    (asset,) = order.get_assets()
    assert isinstance(asset, Asset)
    assert asset.asset_id == ASSET_ORDER_ID


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
def test_should_fail_to_get_assets_for_unfulfilled_order(
    auth_mock, requests_mock, status
):
    order_response = {"id": ORDER_ID, "status": status}
    url_order_info = f"{API_HOST}/v2/orders/{ORDER_ID}"
    requests_mock.get(url=url_order_info, json=order_response)
    order = Order(auth=auth_mock, order_id=ORDER_ID)
    with pytest.raises(ValueError):
        order.get_assets()


@pytest.mark.live
def test_get_assets_live(auth_live, catalog_order_parameters):
    order_instance = Order(auth=auth_live, order_id=ORDER_ID)
    assets = order_instance.get_assets()
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == ASSET_ORDER_ID


def test_place_order(
    catalog_order_parameters, auth_mock, order_mock, requests_mock
):
    requests_mock.post(
        url=f"{API_HOST}/v2/orders?workspaceId={WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": ORDER_ID}],
            "errors": [],
        },
    )
    order = Order.place(auth_mock, catalog_order_parameters)
    assert isinstance(order, Order)
    assert order.order_id == ORDER_ID
    assert order.order_parameters == catalog_order_parameters


def test_place_order_fails_if_response_contains_error(
    catalog_order_parameters, auth_mock, order_mock, requests_mock
):
    error_content = "test error"
    requests_mock.post(
        url=f"{API_HOST}/v2/orders?workspaceId={WORKSPACE_ID}",
        json={
            "results": [],
            "errors": [{"message": error_content}],
        },
    )
    with pytest.raises(ValueError) as err:
        Order.place(auth_mock, catalog_order_parameters)
    assert error_content in str(err.value)


@pytest.mark.skip(reason="Placing orders costs credits.")
@pytest.mark.live
def test_place_order_live(auth_live, catalog_order_parameters):
    order = Order.place(auth_live, catalog_order_parameters)
    assert order.status == "PLACED"
    assert order.order_parameters == catalog_order_parameters


def test_track_status_running(order_mock, requests_mock):
    del order_mock._info

    url_job_info = f"{API_HOST}/v2/orders/{order_mock.order_id}"

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

    url_job_info = f"{API_HOST}/v2/orders/{order_mock.order_id}"
    requests_mock.get(url=url_job_info, json={"status": status})

    order_status = order_mock.track_status()
    assert order_status == status


@pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
def test_track_status_fail(order_mock, status, requests_mock):
    del order_mock._info

    url_job_info = f"{API_HOST}/v2/orders/{order_mock.order_id}"
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
    url_order_estimation = f"{API_HOST}/v2/orders/estimate"
    requests_mock.post(url=url_order_estimation, json=expected_payload)
    estimation = Order.estimate(auth_mock, catalog_order_parameters)
    assert isinstance(estimation, int)
    assert estimation == 100


@pytest.mark.live
def test_estimate_order_live(catalog_order_parameters, auth_live):
    estimation = Order.estimate(
        auth_live, order_parameters=catalog_order_parameters
    )
    assert isinstance(estimation, int)
    assert estimation == 100
