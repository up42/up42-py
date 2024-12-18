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
ERRORS = {
    "errors": [
        {
            "index": ERROR.index,
            "message": ERROR.message,
            "details": ERROR.details,
        }
    ],
}
ESTIMATION = {
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
PLACEMENT = {
    "results": [
        {
            "index": ORDER_REFERENCE.index,
            "id": constants.ORDER_ID,
        }
    ]
} | ERRORS
BATCH_COST = order_template.BatchCost(items=[COST, ERROR], credits=COST.credits, size=COST.size, unit=COST.unit)


class TestOrderReference:
    def test_should_provide_order(self):
        with mock.patch("up42.order.Order.get") as get_order:
            get_order.return_value = mock.sentinel
            assert ORDER_REFERENCE.order == mock.sentinel
            get_order.assert_called_with(constants.ORDER_ID)


class TestBatchOrderTemplate:
    def test_should_place(self, requests_mock: req_mock.Mocker):
        estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
        requests_mock.post(url=estimate_url, json=ESTIMATION)
        placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
        requests_mock.post(url=placement_url, json=PLACEMENT)
        template = order_template.BatchOrderTemplate(
            data_product_id=constants.DATA_PRODUCT_ID,
            display_name=DISPLAY_NAME,
            tags=TAGS,
            features=FEATURES,
            params=PARAMS,
        )
        assert template.cost == BATCH_COST
        assert template.place() == [ORDER_REFERENCE, ERROR]
