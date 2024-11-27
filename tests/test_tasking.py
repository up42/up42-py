import urllib.parse
from typing import Any, List, Optional
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42 import tasking

from . import helpers
from .fixtures import fixtures_globals as constants

ACQ_START = "2014-01-01T00:00:00"
ACQ_END = "2022-12-31T23:59:59"
ORDER_NAME = "order-name"
POINT = {"type": "Point", "coordinates": (1.0, 2.0)}
POLYGON = {
    "type": "Polygon",
    "coordinates": (
        (
            (1.0, 1.0),
            (2.0, 1.0),
            (2.0, 2.0),
            (1.0, 2.0),
            (1.0, 1.0),
        ),
    ),
}

QUOTATION_ID = "805b1f27-1025-43d2-90d0-0bd3416238fb"
FEASIBILITY_ID = "6f93f754-5594-42da-b6af-9064225b89e9"


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth.session = requests.session()
        yield


class TestTasking:
    @pytest.fixture
    def tasking_obj(self) -> tasking.Tasking:
        return tasking.Tasking()

    @pytest.mark.parametrize(
        "geometry",
        [
            POINT,
            POLYGON,
        ],
        ids=["point_aoi", "polygon_aoi"],
    )
    @pytest.mark.parametrize(
        "tags",
        [
            ["tag"],
            None,
        ],
        ids=[
            "tags:Value",
            "tags:None",
        ],
    )
    def test_should_construct_order_parameters(
        self,
        requests_mock: req_mock.Mocker,
        tasking_obj: tasking.Tasking,
        geometry: tasking.Geometry,
        tags: Optional[List[str]],
    ):
        required_property = "any-property"
        url_schema = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
        requests_mock.get(
            url_schema,
            json={
                "required": [required_property],
                "properties": {
                    required_property: {
                        "type": "string",
                        "title": "string",
                        "format": "string",
                    }
                },
            },
        )
        order_parameters = tasking_obj.construct_order_parameters(
            data_product_id=constants.DATA_PRODUCT_ID,
            name=ORDER_NAME,
            acquisition_start=ACQ_START,
            acquisition_end=ACQ_END,
            geometry=geometry,
            tags=tags,
        )
        expected = {
            "params": {
                "displayName": ORDER_NAME,
                "acquisitionStart": ACQ_START + "Z",
                "acquisitionEnd": ACQ_END + "Z",
                "geometry": geometry,
                required_property: None,
            },
            "dataProduct": constants.DATA_PRODUCT_ID,
        } | ({"tags": tags} if tags else {})
        assert order_parameters == expected

    @pytest.mark.parametrize("quotation_id", [None, QUOTATION_ID])
    @pytest.mark.parametrize("workspace_id", [None, constants.WORKSPACE_ID])
    @pytest.mark.parametrize("order_id", [None, constants.ORDER_ID])
    @pytest.mark.parametrize("decision", [None, ["ACCEPTED", "REJECTED", "NOT_DECIDED"], ["ACCEPTED"]])
    @pytest.mark.parametrize("descending", [False, True])
    def test_should_get_quotations(
        self,
        requests_mock: req_mock.Mocker,
        tasking_obj: tasking.Tasking,
        quotation_id: Optional[str],
        workspace_id: Optional[str],
        order_id: Optional[str],
        decision: Optional[List[tasking.QuotationStatus]],
        descending: bool,
    ):
        query_params: dict[str, Any] = {"sort": "createdAt,desc" if descending else "createdAt,asc"}
        if quotation_id:
            query_params["id"] = quotation_id
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if order_id:
            query_params["orderId"] = order_id
        if decision:
            query_params["decision"] = decision
        base_url = f"{constants.API_HOST}/v2/tasking/quotation"
        expected = [{"id": f"id{idx}"} for idx in [1, 2, 3, 4]]
        for page in [0, 1]:
            query_params["page"] = page
            query = urllib.parse.urlencode(query_params, doseq=True, safe="")
            url = base_url + (query and f"?{query}")
            offset = page * 2
            response = {
                "content": expected[offset : offset + 2],  # noqa: E203
                "totalPages": 2,
            }
            requests_mock.get(url=url, json=response)

        quotations = tasking_obj.get_quotations(
            quotation_id=quotation_id,
            workspace_id=workspace_id,
            order_id=order_id,
            decision=decision,
            descending=descending,
        )
        assert quotations == expected

    @pytest.mark.parametrize("decision", ["ACCEPTED", "REJECTED"])
    def test_should_decide_quotation(
        self,
        requests_mock: req_mock.Mocker,
        tasking_obj: tasking.Tasking,
        decision: tasking.QuotationDecision,
    ):
        payload = {"decision": decision}
        url = f"{constants.API_HOST}/v2/tasking/quotation/{QUOTATION_ID}"
        expected = {
            "id": QUOTATION_ID,
            "decision": decision,
        }
        requests_mock.patch(
            url=url,
            json=expected,
            additional_matcher=helpers.match_request_body(payload),
        )
        assert tasking_obj.decide_quotation(quotation_id=QUOTATION_ID, decision=decision) == expected

    def test_fails_to_decide_quotation_with_wrong_value(
        self,
        tasking_obj: tasking.Tasking,
    ):
        with pytest.raises(tasking.InvalidDecision):
            tasking_obj.decide_quotation(QUOTATION_ID, decision="ANYTHING")  # type: ignore

    @pytest.mark.parametrize("feasibility_id", [None, QUOTATION_ID])
    @pytest.mark.parametrize("workspace_id", [None, constants.WORKSPACE_ID])
    @pytest.mark.parametrize("order_id", [None, constants.ORDER_ID])
    @pytest.mark.parametrize("decision", [None, ["ACCEPTED", "NOT_DECIDED"], ["ACCEPTED"]])
    @pytest.mark.parametrize("descending", [False, True])
    def test_should_get_feasibility(
        self,
        requests_mock: req_mock.Mocker,
        tasking_obj: tasking.Tasking,
        feasibility_id: Optional[str],
        workspace_id: Optional[str],
        order_id: Optional[str],
        decision: Optional[List[tasking.FeasibilityDecision]],
        descending: bool,
    ):
        query_params: dict[str, Any] = {"sort": "createdAt," + ("desc" if descending else "asc")}
        if feasibility_id:
            query_params["id"] = feasibility_id
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if order_id:
            query_params["orderId"] = order_id
        if decision:
            query_params["decision"] = decision
        base_url = f"{constants.API_HOST}/v2/tasking/feasibility"
        expected = [{"id": f"id{idx}"} for idx in [1, 2, 3, 4]]
        for page in [0, 1]:
            query_params["page"] = page
            query = urllib.parse.urlencode(query_params, doseq=True, safe="")
            url = base_url + (query and f"?{query}")
            offset = page * 2
            response = {
                "content": expected[offset : offset + 2],  # noqa: E203
                "totalPages": 2,
            }
            requests_mock.get(url=url, json=response)

        studies = tasking_obj.get_feasibility(
            feasibility_id=feasibility_id,
            workspace_id=workspace_id,
            order_id=order_id,
            decision=decision,
            descending=descending,
        )
        assert studies == expected

    def test_should_choose_feasibility(self, requests_mock: req_mock.Mocker, tasking_obj: tasking.Tasking):
        accepted_option_id = "accepted-option-id"
        payload = {"acceptedOptionId": accepted_option_id}
        url = f"{constants.API_HOST}/v2/tasking/feasibility/{FEASIBILITY_ID}"
        expected = {
            "id": FEASIBILITY_ID,
            "decisionOption": {
                "id": accepted_option_id,
            },
        }
        requests_mock.patch(
            url=url,
            json=expected,
            additional_matcher=helpers.match_request_body(payload),
        )
        assert (
            tasking_obj.choose_feasibility(
                feasibility_id=FEASIBILITY_ID,
                accepted_option_id=accepted_option_id,
            )
            == expected
        )
