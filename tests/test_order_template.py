from unittest import mock

import geojson  # type: ignore

# import pytest
# import requests
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

    # def test_should_raise_eula_not_accepted_error(self, requests_mock: req_mock.Mocker):
    #     """Test that EulaNotAcceptedError is raised with clear message when EULA is not accepted"""
    #     estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
    #     requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
    #     placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
    #     eula_id = "95d6fff5-493c-4118-8edf-3096e73eda12"
    #     error_response = {
    #         "status": 451,
    #         "title": f"EULA {eula_id} is not accepted. Please go to Up42 Console/EULA management "
    #         "(https://console.up42.dev/settings/eula) to manage the settings.",
    #         "detail": None,
    #     }
    #     requests_mock.post(url=placement_url, status_code=451, json=error_response)
    #
    #     template = order_template.BatchOrderTemplate(
    #         data_product_id=constants.DATA_PRODUCT_ID,
    #         display_name=DISPLAY_NAME,
    #         features=FEATURES,
    #         params=PARAMS,
    #     )
    #
    #     with pytest.raises(order_template.EulaNotAcceptedError) as exc_info:
    #         template.place()
    #
    #     assert eula_id in str(exc_info.value)
    #     assert exc_info.value.eula_id == eula_id
    #     assert "EULA management" in str(exc_info.value)
    #
    # def test_should_raise_access_restricted_error(self, requests_mock: req_mock.Mocker):
    #     """Test that AccessRestrictedError is raised with clear message when access is restricted"""
    #     estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
    #     requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
    #     placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
    #     collection_name = "pixxel-tasking"
    #     account_id = "3c86279b-610a-4dba-ad12-abe3bdc51428"
    #     error_response = {
    #         "status": 451,
    #         "title": f"Access to collection {collection_name} is restricted for account {account_id}. "
    #         f"To request access please go to Up42 Console/Access Requests "
    #         f"https://console.up42.com/settings/access?collection={collection_name}",
    #         "detail": None,
    #     }
    #     requests_mock.post(url=placement_url, status_code=451, json=error_response)
    #
    #     template = order_template.BatchOrderTemplate(
    #         data_product_id=constants.DATA_PRODUCT_ID,
    #         display_name=DISPLAY_NAME,
    #         features=FEATURES,
    #         params=PARAMS,
    #     )
    #
    #     with pytest.raises(order_template.AccessRestrictedError) as exc_info:
    #         template.place()
    #
    #     assert collection_name in str(exc_info.value)
    #     assert exc_info.value.collection == collection_name
    #     assert "Access Requests" in str(exc_info.value)
    #
    # def test_should_handle_451_error_without_json_body(self, requests_mock: req_mock.Mocker):
    #     """Test that generic 451 error is handled when response has no JSON body"""
    #     estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
    #     requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
    #     placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
    #     requests_mock.post(url=placement_url, status_code=451, text="Unavailable For Legal Reasons")
    #
    #     template = order_template.BatchOrderTemplate(
    #         data_product_id=constants.DATA_PRODUCT_ID,
    #         display_name=DISPLAY_NAME,
    #         features=FEATURES,
    #         params=PARAMS,
    #     )
    #
    #     with pytest.raises(requests.HTTPError) as exc_info:
    #         template.place()
    #
    #     assert exc_info.value.response.status_code == 451
    #
    # def test_should_propagate_other_http_errors(self, requests_mock: req_mock.Mocker):
    #     """Test that non-451 HTTP errors are propagated unchanged"""
    #     estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
    #     requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
    #     placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
    #     requests_mock.post(url=placement_url, status_code=500, json={"error": "Internal Server Error"})
    #
    #     template = order_template.BatchOrderTemplate(
    #         data_product_id=constants.DATA_PRODUCT_ID,
    #         display_name=DISPLAY_NAME,
    #         features=FEATURES,
    #         params=PARAMS,
    #     )
    #
    #     with pytest.raises(requests.HTTPError) as exc_info:
    #         template.place()
    #
    #     assert exc_info.value.response.status_code == 500
    #
    # def test_should_handle_generic_451_error(self, requests_mock: req_mock.Mocker):
    #     """Test that generic 451 error without specific keywords is handled"""
    #     estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
    #     requests_mock.post(url=estimate_url, json=ESTIMATE_PAYLOAD)
    #     placement_url = f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}"
    #     error_response = {
    #         "status": 451,
    #         "title": "Some other legal restriction",
    #         "detail": None,
    #     }
    #     requests_mock.post(url=placement_url, status_code=451, json=error_response)
    #
    #     template = order_template.BatchOrderTemplate(
    #         data_product_id=constants.DATA_PRODUCT_ID,
    #         display_name=DISPLAY_NAME,
    #         features=FEATURES,
    #         params=PARAMS,
    #     )
    #
    #     with pytest.raises(order_template.EulaNotAcceptedError) as exc_info:
    #         template.place()
    #
    #     assert "Some other legal restriction" in str(exc_info.value)
