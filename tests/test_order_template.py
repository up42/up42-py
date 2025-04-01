from unittest import mock

import geojson  # type: ignore
import requests_mock as req_mock

from tests import constants
from up42 import order_template

DISPLAY_NAME = "display-name"
TAGS = ["some", "tags"]
FEATURES = geojson.FeatureCollection(features=[geojson.Feature(geometry={"type": "Point", "coordinates": [0, 0]})])
PARAMS = {"some": "params"}
PAYLOAD = {
    "displayName": DISPLAY_NAME,
    "dataProduct": constants.DATA_PRODUCT_ID,
    "tags": TAGS,
    "featureCollection": FEATURES,
    "params": PARAMS,
}
ERROR = order_template.OrderError(index=1, message="Failed", details="Invalid geometry")
COST = order_template.OrderCost(index=0, credits=10, size=50, unit="SQ_KM")
ORDER_REFERENCE = order_template.OrderReference(index=0, id=constants.ORDER_ID)
ESTIMATE = order_template.Estimate(items=[COST, ERROR], credits=COST.credits, size=COST.size, unit=COST.unit)
ERRORS = {
    "errors": [
        {
            "index": ERROR.index,
            "message": ERROR.message,
            "details": ERROR.details,
        }
    ],
}
ESTIMATE_PAYLOAD = {
    "summary": {
        "totalCredits": COST.credits,
        "totalSize": COST.size,
        "unit": COST.unit,
    },
    "results": [
        {
            "index": COST.index,
            "credits": COST.credits,
            "size": COST.size,
            "unit": COST.unit,
        }
    ],
} | ERRORS
PLACEMENT_PAYLOAD = {
    "results": [
        {
            "index": ORDER_REFERENCE.index,
            "id": constants.ORDER_ID,
        }
    ]
} | ERRORS


class TestOrderReference:
    def test_should_provide_order(self):
        with mock.patch("up42.order.Order.get") as get_order:
            get_order.return_value = mock.sentinel
            assert ORDER_REFERENCE.order == mock.sentinel
            get_order.assert_called_with(constants.ORDER_ID)


class TestBatchOrderTemplate:
    def test_should_place(self, requests_mock: req_mock.Mocker):
        estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
        requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
        placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
        requests_mock.post(url=placement_url, json=PLACEMENT_PAYLOAD)
        template = order_template.BatchOrderTemplate(
            data_product_id=constants.DATA_PRODUCT_ID,
            display_name=DISPLAY_NAME,
            tags=TAGS,
            features=FEATURES,
            params=PARAMS,
        )
        expected_payload = {
            "dataProduct": constants.DATA_PRODUCT_ID,
            "displayName": DISPLAY_NAME,
            "params": PARAMS,
            "tags": TAGS,
            "featureCollection": FEATURES,
        }
        assert template._payload == expected_payload  # pylint: disable=protected-access
        assert template.estimate == ESTIMATE
        assert template.place() == [ORDER_REFERENCE, ERROR]

    def test_should_place_without_tags(self, requests_mock: req_mock.Mocker):
        estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
        requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
        placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
        requests_mock.post(url=placement_url, json=PLACEMENT_PAYLOAD)
        template = order_template.BatchOrderTemplate(
            data_product_id=constants.DATA_PRODUCT_ID,
            display_name=DISPLAY_NAME,
            features=FEATURES,
            params=PARAMS,
        )
        expected_payload = {
            "dataProduct": constants.DATA_PRODUCT_ID,
            "displayName": DISPLAY_NAME,
            "params": PARAMS,
            "featureCollection": FEATURES,
        }
        assert template._payload == expected_payload  # pylint: disable=protected-access
        assert template.estimate == ESTIMATE
        assert template.place() == [ORDER_REFERENCE, ERROR]
