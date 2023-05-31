from pathlib import Path
import json

import pytest

from .fixtures_globals import DATA_PRODUCT_ID

from ..context import (
    Tasking,
)


@pytest.fixture()
def tasking_mock(auth_mock, requests_mock):
    url_data_product_schema = f"{auth_mock._endpoint()}/orders/schema/{DATA_PRODUCT_ID}"
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/data_product_schema_tasking.json"
    ) as json_file:
        json_data_product_schema = json.load(json_file)
        requests_mock.get(url=url_data_product_schema, json=json_data_product_schema)

    url_get_quotations_mp1 = (
        f"{auth_mock._endpoint()}/v2/tasking/quotation?page=0&sort=createdAt,desc"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_multi_page_01.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(url=url_get_quotations_mp1, json=json_data_get_quotation)

    url_get_quotations_mp2 = (
        f"{auth_mock._endpoint()}/v2/tasking/quotation?page=1&sort=createdAt,desc"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_multi_page_02.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(url=url_get_quotations_mp2, json=json_data_get_quotation)

    url_get_quotations_mp3 = (
        f"{auth_mock._endpoint()}/v2/tasking/quotation?page=2&sort=createdAt,desc"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_multi_page_03.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(url=url_get_quotations_mp3, json=json_data_get_quotation)

    sorting = "page=0&sort=createdAt,desc"
    workspace = "80357ed6-9fa2-403c-9af0-65e4955d4816"
    decision = "ACCEPTED"
    endpoint = "/v2/tasking/quotation?"

    url_get_quotations_workspace_filtered = (
        f"{auth_mock._endpoint()}{endpoint}{sorting}&workspaceId={workspace}"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_workspace_id.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(
            url=url_get_quotations_workspace_filtered, json=json_data_get_quotation
        )

    url_get_quotations_decision_filtered = (
        f"{auth_mock._endpoint()}{endpoint}{sorting}&decision={decision}"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_decision_ACCEPTED.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(
            url=url_get_quotations_decision_filtered, json=json_data_get_quotation
        )
    
    
    wrong_id_response_json = json.dumps({
        'status': 404, 
        'title': "Resource (Quotation) not found with Id='296ef1b0-d890-430d-8d14-e9b579ab08ba'.", 
        'detail': None
    })
    decide_quotation_endpoint = "/v2/tasking/quotation/296ef1b0-d890-430d-8d14-e9b579ab08ba"
    url_decide_quotation_fail = (
        f"{auth_mock._endpoint()}{decide_quotation_endpoint}"
    )
    requests_mock.patch(
            url=url_decide_quotation_fail, 
            status_code = 404,
            json=wrong_id_response_json
    )
    
    decide_quotation_endpoint = "/v2/tasking/quotation/296ef1b0-d890-430d-8d14-e9b579ab08bd"
    url_decide_quotation_accepted = (
        f"{auth_mock._endpoint()}{decide_quotation_endpoint}"
    )
    accepted_id_response_json = json.dumps({
        'status': 405, 
        'title': 'Resource (Quotation) is write-protected.', 
        'detail': None
    })
    requests_mock.patch(
            url=url_decide_quotation_accepted, 
            status_code = 405,
            json=accepted_id_response_json
    )

    return Tasking(auth=auth_mock)


@pytest.fixture()
def tasking_live(auth_live):
    tasking = Tasking(auth=auth_live)
    return tasking
