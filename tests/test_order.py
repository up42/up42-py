import json
import os
from pathlib import Path

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


@pytest.fixture
def order_parameters():
    return {
        "dataProduct": "b1f8c48e-d16b-44c4-a1bb-5e8a24892e69",
        "displayName": "Pléiades Neo over North America",
        "tags": ["project-7"],
        "params": {
            "id": "14e49010-9fab-4ba8-b4c5-ed929a083400",
            "extraDescription": "Order Description",
            "radiometricProcessing": "HH",
            "acquisitionMode": "spotlight",
            "acquisitionEnd": "2022-05-18T22:00:00.000Z",
            "acquisitionStart": "2022-05-17T22:00:00.000Z",
        },
        "featureCollection": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
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
                    "properties": {},
                }
            ],
        },
    }


def test_place_order(order_parameters, auth_mock, requests_mock, order_mock):
    requests_mock.post(
        url=f"{auth_mock._endpoint()}/v2/orders?workspaceId={WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": ORDER_ID}],
            "error": [],
        },
    )
    order = Order.place(auth_mock, order_parameters)
    assert isinstance(order, list)
    assert order[0].order_id == ORDER_ID
    assert order[0].order_parameters == order_parameters


def test_place_order_no_id(order_parameters, auth_mock, order_mock, requests_mock):
    requests_mock.post(
        url=f"{auth_mock._endpoint()}/v2/orders?workspaceId={WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "xyz": 892}],
            "error": [],
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
    url_order_estimation = f"{auth_mock._endpoint()}/v2/orders/estimate"
    expected_payload = {
        "summary": {"totalCredits": 38, "totalSize": 0.1, "unit": "SQ_KM"},
        "results": [{"index": 0, "credits": 38, "unit": "SQ_KM", "size": 0.1}],
        "errors": [],
    }
    expected_output = {
        "errors": [],
        "results": [{"credits": 38, "index": 0, "size": 0.1, "unit": "SQ_KM"}],
        "summary": {"totalCredits": 38, "totalSize": 0.1, "unit": "SQ_KM"},
    }
    requests_mock.post(url=url_order_estimation, json=expected_payload)
    estimation = Order.estimate(auth_mock, order_parameters)
    assert isinstance(estimation, dict)
    assert estimation == expected_output


@pytest.mark.parametrize(
    "expected_payload",
    [
        {
            "data": None,
            "error": {
                "code": 400,
                "message": "AOI area must be more than 0.1 km².",
                "details": None,
            },
        },
        {
            "summary": {},
            "results": [],
            "errors": [],
        },
    ],
    ids=[
        "Sc1: Error log with http response",
        "Sc2: Error log total_estimation None",
    ],
)
def test_estimate_order_fail(
    order_parameters, auth_mock, requests_mock, expected_payload
):
    url_order_estimation = f"{auth_mock._endpoint()}/v2/orders/estimate"
    requests_mock.post(url=url_order_estimation, json=expected_payload)
    with pytest.raises(ValueError):
        Order.estimate(auth_mock, order_parameters)


@pytest.mark.live
def test_estimate_order_live(order_parameters, auth_live):
    expected_output = {
        "errors": [],
        "results": [{"credits": 38, "index": 0, "size": 0.1, "unit": "SQ_KM"}],
        "summary": {"totalCredits": 38, "totalSize": 0.1, "unit": "SQ_KM"},
    }
    estimation = Order.estimate(auth_live, order_parameters=order_parameters)
    assert isinstance(estimation, dict)
    assert estimation == expected_output
