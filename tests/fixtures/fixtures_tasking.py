from pathlib import Path
import json

import pytest

from .fixtures_globals import (
    DATA_PRODUCT_ID,
    WORKSPACE_ID,
    QUOTATION_ID,
)

from ..context import (
    Tasking,
)

QUOTATION_ENDPOINT = "/v2/tasking/quotation"


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
        f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?page=0&sort=createdAt,desc"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_multi_page_01.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(url=url_get_quotations_mp1, json=json_data_get_quotation)

    url_get_quotations_mp2 = (
        f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?page=1&sort=createdAt,desc"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_multi_page_02.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(url=url_get_quotations_mp2, json=json_data_get_quotation)

    url_get_quotations_mp3 = (
        f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?page=2&sort=createdAt,desc"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_multi_page_03.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(url=url_get_quotations_mp3, json=json_data_get_quotation)

    sorting = "page=0&sort=createdAt,desc"

    url_get_quotations_workspace_filtered = (
        f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?{sorting}&workspaceId={WORKSPACE_ID}"
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
        f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?{sorting}&decision=ACCEPTED"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_decision_ACCEPTED.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(
            url=url_get_quotations_decision_filtered, json=json_data_get_quotation
        )
        url_get_quotations_decision_filtered = (
            f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?{sorting}&decision=ACCEPTED"
        )

    desicion_filter = "&decision=ACCEPTED&decision=REJECTED"
    url_get_quotations_decision_filtered = (
        f"{auth_mock._endpoint()}{QUOTATION_ENDPOINT}?{sorting}{desicion_filter}"
    )
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/tasking_data/get_quotations_decision_ACCEPTED.json"
    ) as json_file:
        json_data_get_quotation = json.load(json_file)
        requests_mock.get(
            url=url_get_quotations_decision_filtered, json=json_data_get_quotation
        )

    wrong_id_response_json = json.dumps(
        {"status": 404, "title": "Resource does not exist.", "detail": {}}
    )
    decide_quotation_endpoint = f"/v2/tasking/quotation/{QUOTATION_ID}-01"
    url_decide_quotation_fail = f"{auth_mock._endpoint()}{decide_quotation_endpoint}"
    requests_mock.patch(
        url=url_decide_quotation_fail, status_code=404, json=wrong_id_response_json
    )

    decide_quotation_endpoint = f"/v2/tasking/quotation/{QUOTATION_ID}-02"
    url_decide_quotation_accepted = (
        f"{auth_mock._endpoint()}{decide_quotation_endpoint}"
    )
    accepted_id_response_json = json.dumps(
        {
            "status": 405,
            "title": "Resource (Quotation) is write-protected.",
            "detail": {},
        }
    )
    requests_mock.patch(
        url=url_decide_quotation_accepted,
        status_code=405,
        json=accepted_id_response_json,
    )

    return Tasking(auth=auth_mock)


@pytest.fixture()
def tasking_live(auth_live):
    tasking = Tasking(auth=auth_live)
    return tasking
