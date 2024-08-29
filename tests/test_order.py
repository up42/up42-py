import pytest
import requests_mock as req_mock

from up42 import asset, order

from .fixtures import fixtures_globals as constants
from .fixtures import fixtures_order

ORDER_URL = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
ORDER_TRANSACTION_URL = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"


def test_init(order_mock):
    assert isinstance(order_mock, order.Order)
    assert order_mock.order_id == constants.ORDER_ID


def test_order_info(order_mock):
    assert order_mock.info
    assert order_mock.info["id"] == constants.ORDER_ID


def test_repr(auth_mock):
    order_info = {
        "id": "your_order_id",
        "status": "PLACED",
        "createdAt": "2023-01-01T12:00:00Z",
        "updatedAt": "2023-01-01T12:30:00Z",
    }
    order_placed = order.Order(auth_mock, order_id="your_order_id", order_info=order_info)

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


def test_get_assets_should_search_assets_by_order_id(auth_mock, requests_mock):
    order_response = {"id": constants.ORDER_ID, "status": "FULFILLED"}
    url_order_info = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
    requests_mock.get(url=url_order_info, json=order_response)
    url_asset_info = f"{constants.API_HOST}/v2/assets?search={constants.ORDER_ID}&size=50"
    requests_mock.get(url=url_asset_info, json=fixtures_order.JSON_GET_ASSETS_RESPONSE)
    order_placed = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
    (asset_returned,) = order_placed.get_assets()
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
def test_should_fail_to_get_assets_for_unfulfilled_order(auth_mock, requests_mock, status):
    order_response = {"id": constants.ORDER_ID, "status": status}
    url_order_info = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
    requests_mock.get(url=url_order_info, json=order_response)
    order_placed = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
    with pytest.raises(ValueError):
        order_placed.get_assets()


class TestOrder:
    def test_track_status_running(self, auth_mock, requests_mock):
        placed_response = [
            {
                "json": {
                    "status": "PLACED",
                    "type": "TASKING",
                    "orderDetails": {"subStatus": "NON_STANDARD_RESPONSE"},
                }
            }
        ] * 10
        being_fulfilled_response = [
            {
                "json": {
                    "status": "BEING_FULFILLED",
                    "type": "TASKING",
                    "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
                }
            },
        ] * 10
        fulfilled_response = [
            {
                "json": {
                    "status": "FULFILLED",
                    "type": "TASKING",
                    "orderDetails": {"subStatus": "FEASIBILITY_WAITING_UPLOAD"},
                }
            }
        ]

        status_responses = placed_response
        status_responses.extend(being_fulfilled_response)
        status_responses.extend(fulfilled_response)
        requests_mock.get(ORDER_URL, status_responses)
        order_test = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
        order_status = order_test.track_status(report_time=1)
        assert order_status == "FULFILLED"

    @pytest.mark.parametrize("status", ["FULFILLED"])
    def test_track_status_pass(self, auth_mock, requests_mock, status):
        requests_mock.get(url=ORDER_URL, json={"status": status})
        order_placed = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
        order_status = order_placed.track_status()
        assert order_status == status

    @pytest.mark.parametrize("status", ["FAILED", "FAILED_PERMANENTLY"])
    def test_track_status_fail(self, auth_mock, requests_mock, status):
        requests_mock.get(
            url=ORDER_URL,
            json={"status": status, "type": "ARCHIVE"},
        )
        order_placed = order.Order(auth=auth_mock, order_id=constants.ORDER_ID)
        with pytest.raises(ValueError):
            order_placed.track_status()


class TestOrderTransactions:
    order_parameters_catalog: order.OrderParams = {
        "dataProduct": "some-data-product",
        "params": {"aoi": {"some": "data"}},
    }
    order_parameters_tasking: order.OrderParams = {
        "dataProduct": "some-data-product",
        "params": {"geometry": {"some": "data"}},
    }
    order_parameters = [
        (order_parameters_catalog),
        (order_parameters_tasking),
    ]

    @pytest.mark.parametrize(
        "order_parameters",
        order_parameters,
        ids=["ARCHIVE", "TASKING"],
    )
    def test_should_return_order_estimation(self, auth_mock, requests_mock, order_parameters):
        expected_credits = 100
        estimation_response = {
            "summary": {"totalCredits": expected_credits},
            "errors": [],
        }
        url = f"{constants.API_HOST}/v2/orders/estimate"
        requests_mock.post(url=url, json=estimation_response)
        estimation = order.Order.estimate(auth_mock, order_parameters)
        assert estimation == expected_credits

    @pytest.mark.parametrize(
        "order_parameters",
        order_parameters,
        ids=["ARCHIVE", "TASKING"],
    )
    def test_estimate_order_fails_if_response_contains_error(self, auth_mock, requests_mock, order_parameters):
        estimation_response_with_error = {"errors": [{"message": "test error"}]}
        url = f"{constants.API_HOST}/v2/orders/estimate"
        requests_mock.post(url=url, json=estimation_response_with_error)
        with pytest.raises(KeyError):
            order.Order.estimate(auth_mock, order_parameters)

    @pytest.mark.parametrize(
        "order_parameters",
        order_parameters,
        ids=["ARCHIVE", "TASKING"],
    )
    def test_should_return_order_placed(self, auth_mock, requests_mock: req_mock.Mocker, order_parameters):
        info = {"status": "SOME STATUS"}
        requests_mock.get(
            url=ORDER_URL,
            json=info,
        )
        order_response = {"results": [{"id": constants.ORDER_ID}], "errors": []}
        requests_mock.post(
            url=ORDER_TRANSACTION_URL,
            json=order_response,
        )
        order_placed = order.Order.place(auth_mock, order_parameters, constants.WORKSPACE_ID)
        expected_order = order.Order(auth_mock, order_id=constants.ORDER_ID, order_info=info)
        assert order_placed == expected_order

    @pytest.mark.parametrize(
        "order_parameters",
        order_parameters,
        ids=["ARCHIVE", "TASKING"],
    )
    def test_place_order_fails_if_response_contains_error(self, auth_mock, requests_mock, order_parameters):
        order_response_with_error = {"results": [], "errors": [{"message": "test error"}]}
        requests_mock.post(
            url=ORDER_TRANSACTION_URL,
            json=order_response_with_error,
        )
        with pytest.raises(ValueError) as err:
            order.Order.place(auth_mock, order_parameters, constants.WORKSPACE_ID)
            assert "test error" in str(err.value)
