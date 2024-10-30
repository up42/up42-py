import json
import pathlib

import pytest

from up42 import tasking

from . import fixtures_globals as constants

QUOTATION_ENDPOINT = "/v2/tasking/quotation"


@pytest.fixture()
def tasking_mock(auth_mock, requests_mock):
    url_data_product_schema = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/data_product_schema_phr_tasking.json",
        encoding="utf-8",
    ) as json_file:
        json_data_product_schema = json.load(json_file)
        requests_mock.get(url=url_data_product_schema, json=json_data_product_schema)
    wrong_id_response_json = {
        "status": 404,
        "title": "Resource does not exist.",
        "detail": {},
    }
    decide_quotation_endpoint = f"/v2/tasking/quotation/{constants.QUOTATION_ID}-01"
    url_decide_quotation_fail = f"{constants.API_HOST}{decide_quotation_endpoint}"
    requests_mock.patch(
        url=url_decide_quotation_fail,
        status_code=404,
        json=wrong_id_response_json,
    )

    decide_quotation_endpoint = f"/v2/tasking/quotation/{constants.QUOTATION_ID}-02"
    url_decide_quotation_accepted = f"{constants.API_HOST}{decide_quotation_endpoint}"
    accepted_id_response_json = {
        "status": 405,
        "title": "Resource (Quotation) is write-protected.",
        "detail": {},
    }

    requests_mock.patch(
        url=url_decide_quotation_accepted,
        status_code=405,
        json=accepted_id_response_json,
    )

    return tasking.Tasking(auth=auth_mock)


@pytest.fixture()
def tasking_get_feasibility_mock(auth_mock, requests_mock):
    get_feasibility_page0_url = f"{constants.API_HOST}/v2/tasking/feasibility?page=0&sort=createdAt,desc"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/tasking_data/get_feasibility_multi_page_01.json",
        encoding="utf-8",
    ) as json_file:
        json_data = json.load(json_file)
        requests_mock.get(url=get_feasibility_page0_url, json=json_data)

    get_feasibility_page1_url = f"{constants.API_HOST}/v2/tasking/feasibility?page=1&sort=createdAt,desc"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/tasking_data/get_feasibility_multi_page_02.json",
        encoding="utf-8",
    ) as json_file:
        json_data = json.load(json_file)
        requests_mock.get(url=get_feasibility_page1_url, json=json_data)

    get_feasibility_page2_url = f"{constants.API_HOST}/v2/tasking/feasibility?page=2&sort=createdAt,desc"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/tasking_data/get_feasibility_multi_page_03.json",
        encoding="utf-8",
    ) as json_file:
        json_data = json.load(json_file)
        requests_mock.get(url=get_feasibility_page2_url, json=json_data)

    get_feasibility_decision_param = (
        f"{constants.API_HOST}/v2/tasking/feasibility?" "page=0&sort=createdAt,desc&decision=NOT_DECIDED"
    )
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/tasking_data/get_feasibility_NOT_DECIDED.json",
        encoding="utf-8",
    ) as json_file:
        json_data = json.load(json_file)
        requests_mock.get(url=get_feasibility_decision_param, json=json_data)

    return tasking.Tasking(auth=auth_mock)


@pytest.fixture()
def tasking_choose_feasibility_mock(auth_mock, requests_mock):
    wrong_feasibility_url = f"{constants.API_HOST}/v2/tasking/feasibility/{constants.WRONG_FEASIBILITY_ID}"
    response = {
        "status": 404,
        "title": "Resource (FeasibilityStudy) not found with Id='296ef160-7890-430d-8d14-e9b579ab08ba'.",
        "detail": {},
    }
    requests_mock.patch(url=wrong_feasibility_url, status_code=404, json=response)

    choose_feasibility_url = f"{constants.API_HOST}/v2/tasking/feasibility/{constants.TEST_FEASIBILITY_ID}"
    response = {
        "status": 405,
        "title": "Resource (FeasibilityStudy) is write-protected.",
        "detail": {},
    }
    requests_mock.patch(url=choose_feasibility_url, status_code=405, json=response)
    return tasking.Tasking(auth=auth_mock)
