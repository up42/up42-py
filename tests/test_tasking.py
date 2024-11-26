import json
import pathlib
import urllib.parse
from typing import Any, List, Optional
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42 import auth as up42_auth
from up42 import tasking

from . import helpers
from .fixtures import fixtures_globals as constants

with open(
    pathlib.Path(__file__).resolve().parent / "mock_data/search_params_simple.json",
    encoding="utf-8",
) as json_file:
    mock_search_parameters = json.load(json_file)


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


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth.session = requests.session()
        yield


class TestTasking:
    @pytest.fixture
    def tasking_obj(self, auth_mock: up42_auth.Auth) -> tasking.Tasking:
        return tasking.Tasking(auth=auth_mock)

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

    @pytest.mark.parametrize("quotation_id", [None, constants.QUOTATION_ID])
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

        next_response = {
            "content": [{"id": f"id{idx}"} for idx in [3, 4]],
            "totalPages": 2,
        }
        query_params["page"] += 1
        query = urllib.parse.urlencode(query_params, doseq=True, safe="")
        next_url = base_url + (query and f"?{query}")
        requests_mock.get(url=next_url, json=next_response)

        expected = [{"id": f"id{idx}"} for idx in [1, 2, 3, 4]]

        quotations = tasking_obj.get_quotations(
            quotation_id=quotation_id,
            workspace_id=workspace_id,
            order_id=order_id,
            decision=decision,
            descending=descending,
        )
        assert len(quotations) == 4
        assert quotations == expected

    def test_should_decide_quotation(
        self,
        requests_mock: req_mock.Mocker,
        tasking_obj: tasking.Tasking,
    ):
        decision: tasking.QuotationDecision = "ACCEPTED"
        decision_payload = {"decision": decision}
        url = f"{constants.API_HOST}/v2/tasking/quotation/{constants.QUOTATION_ID}"
        expected = {
            "id": constants.QUOTATION_ID,
            "decision": decision,
        }
        requests_mock.put(
            url=url,
            json=expected,
            additional_matcher=helpers.match_request_body(decision_payload),
        )
        assert tasking_obj.decide_quotation(quotation_id=constants.QUOTATION_ID, decision=decision) == expected

    def test_fails_decide_quotation_with_wrong_value(
        self,
        tasking_obj: tasking.Tasking,
    ):
        with pytest.raises(tasking.InvalidDecision, match="Possible decisions are only ACCEPTED or REJECTED."):
            tasking_obj.decide_quotation(constants.QUOTATION_ID, decision="ANYTHING")  # type: ignore


def test_get_feasibility(tasking_get_feasibility_mock):
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility()
    assert len(feasibility_studies) == 26
    assert list(feasibility_studies[0].keys()) == [
        "id",
        "createdAt",
        "updatedAt",
        "accountId",
        "workspaceId",
        "orderId",
        "type",
        "options",
        "decision",
        "decisionById",
        "decisionByType",
        "decisionAt",
        "decisionOption",
    ]
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility(decision=["NOT_DECIDED"])
    assert len(feasibility_studies) == 1
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility(decision=["some_wrong_string"])
    assert len(feasibility_studies) == 26


def test_choose_feasibility(tasking_choose_feasibility_mock):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_choose_feasibility_mock.choose_feasibility(constants.WRONG_FEASIBILITY_ID, constants.WRONG_OPTION_ID)
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 404

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_choose_feasibility_mock.choose_feasibility(constants.TEST_FEASIBILITY_ID, constants.TEST_OPTION_ID)
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 405
