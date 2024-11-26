import json
import pathlib

import pytest

from up42 import tasking

from . import fixtures_globals as constants


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
