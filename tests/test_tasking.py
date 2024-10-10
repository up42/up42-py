import json
import pathlib
from typing import List, Optional
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42 import auth as up42_auth
from up42 import tasking

from .fixtures import fixtures_globals as constants

with open(
    pathlib.Path(__file__).resolve().parent / "mock_data/search_params_simple.json", encoding="utf-8"
) as json_file:
    mock_search_parameters = json.load(json_file)


POINT_BBOX = (1.0, 2.0, 1.0, 2.0)
START_DATE = "2014-01-01"
END_DATE = "2022-12-31"
POINT_GEOM = {"type": "Point", "coordinates": (1.0, 2.0)}
POLY_GEOM = {
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
        workspace_mock.id = constants.WORKSPACE_ID
        yield


class TestTasking:
    @pytest.fixture(autouse=True)
    def tasking_obj(self, auth_mock: up42_auth.Auth) -> tasking.Tasking:
        return tasking.Tasking(auth=auth_mock)

    @pytest.mark.parametrize(
        "input_geometry",
        [
            (POINT_GEOM),
            (POLY_GEOM),
        ],
        ids=["point_aoi", "feature_aoi"],
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
    def test_construct_order_parameters(
        self,
        requests_mock: req_mock.Mocker,
        tasking_obj: tasking.Tasking,
        input_geometry: Optional[tasking.Geometry],
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
            name="some-name",
            acquisition_start=START_DATE,
            acquisition_end=END_DATE,
            geometry=input_geometry,
            tags=tags,
        )
        expected = {
            "params": {
                "displayName": "some-name",
                "acquisitionStart": "2014-01-01T00:00:00Z",
                "acquisitionEnd": "2022-12-31T23:59:59Z",
                "geometry": input_geometry,
                required_property: None,
            },
            "dataProduct": constants.DATA_PRODUCT_ID,
            **({"tags": tags} if tags else {}),
        }
        assert order_parameters == expected


def test_get_quotations(tasking_mock):
    get_quotations = tasking_mock.get_quotations()
    assert len(get_quotations) == 23
    get_workspace_quotations = tasking_mock.get_quotations(workspace_id=constants.WORKSPACE_ID)
    assert all(quotation["workspaceId"] == constants.WORKSPACE_ID for quotation in get_workspace_quotations)
    get_accepted_quotations = tasking_mock.get_quotations(decision=["ACCEPTED"])
    assert all(quotation["decision"] == "ACCEPTED" for quotation in get_accepted_quotations)
    get_decided_quotations = tasking_mock.get_quotations(decision=["ACCEPTED", "REJECTED"])
    assert all(quotation["decision"] in ["ACCEPTED", "REJECTED"] for quotation in get_decided_quotations)


def test_decide_quotation(tasking_mock):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_mock.decide_quotation(constants.QUOTATION_ID + "-01", "ACCEPTED")
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 404

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_mock.decide_quotation(constants.QUOTATION_ID + "-02", "ACCEPTED")
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 405


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
