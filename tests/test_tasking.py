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
        workspace_mock.id = constants.WORKSPACE_ID
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


# def test_get_quotations(auth_mock, requests_mock: req_mock):
#     QUOTATION_ENDPOINT = "/v2/tasking/quotation"
#     url_get_quotations_mp1 = f"{constants.API_HOST}{QUOTATION_ENDPOINT}?page=0&sort=createdAt,desc"
#     with open(
#         pathlib.Path(__file__).resolve().parents[0] / "mock_data/tasking_data/get_quotations_multi_page_01.json",
#         encoding="utf-8",
#     ) as json_file:
#         json_data_get_quotation = json.load(json_file)
#         requests_mock.get(url=url_get_quotations_mp1, json=json_data_get_quotation)

#     url_get_quotations_mp2 = f"{constants.API_HOST}{QUOTATION_ENDPOINT}?page=1&sort=createdAt,desc"
#     with open(
#         pathlib.Path(__file__).resolve().parents[0] / "mock_data/tasking_data/get_quotations_multi_page_02.json",
#         encoding="utf-8",
#     ) as json_file:
#         json_data_get_quotation = json.load(json_file)
#         requests_mock.get(url=url_get_quotations_mp2, json=json_data_get_quotation)
#     url_get_quotations_mp3 = f"{constants.API_HOST}{QUOTATION_ENDPOINT}?page=2&sort=createdAt,desc"
#     with open(
#         pathlib.Path(__file__).resolve().parents[0] / "mock_data/tasking_data/get_quotations_multi_page_03.json",
#         encoding="utf-8",
#     ) as json_file:
#         json_data_get_quotation = json.load(json_file)
#         requests_mock.get(url=url_get_quotations_mp3, json=json_data_get_quotation)
#     get_quotations = tasking.Tasking(auth_mock).get_quotations()
#     assert len(get_quotations) == 23


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
