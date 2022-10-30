import json
from pathlib import Path
import copy

import pytest


@pytest.fixture()
def credits_history_mock(auth_mock, requests_mock):
    with open(
        Path(__file__).resolve().parents[1] / "mock_data/credits_history.json"
    ) as json_file:
        credits_history_response_json = json.load(json_file)
    response_json = copy.deepcopy(credits_history_response_json)
    url_get_credits_history = f"{auth_mock._endpoint()}/accounts/me/credits/history"
    requests_mock.get(
        url=url_get_credits_history,
        json=response_json,
    )
    return auth_mock


@pytest.fixture()
def credits_history_pagination_mock(auth_mock, requests_mock):
    with open(
        Path(__file__).resolve().parents[1] / "mock_data/credits_history.json"
    ) as json_file:
        credits_history_response_json = json.load(json_file)

    response_json = copy.deepcopy(credits_history_response_json)
    temp_content = copy.deepcopy(response_json["data"]["content"])
    pagination_response_json = copy.deepcopy(response_json)
    pagination_response_json["data"]["last"] = False
    pagination_response_json["data"]["content"] = temp_content * 200
    url_get_credits_history_size = (
        f"{auth_mock._endpoint()}/accounts/me/credits/history?page=0"
    )
    requests_mock.get(
        url=url_get_credits_history_size,
        json=pagination_response_json,
    )
    # Page 2
    pagination_response_json_last = copy.deepcopy(response_json)
    pagination_response_json_last["data"]["last"] = True
    pagination_response_json_last["data"]["content"] = temp_content * 50
    url_get_credits_history_size_last = (
        f"{auth_mock._endpoint()}/accounts/me/credits/history?page=1"
    )
    requests_mock.get(
        url=url_get_credits_history_size_last,
        json=pagination_response_json_last,
    )
    return auth_mock
