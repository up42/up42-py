import io
import json
from pathlib import Path

import pytest
import requests

from .context import Auth

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
)
from .fixtures import TOKEN, PROJECT_ID, PROJECT_APIKEY, WORKSPACE_ID


def test_auth_kwargs():
    auth = Auth(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        env="abc",
        authenticate=False,
        retry=False,
    )
    assert auth.env == "abc"
    assert not auth.authenticate
    assert not auth.retry


def test_no_credentials_raises(auth_mock):
    auth_mock.project_id = None
    auth_mock.project_api_key = None
    with pytest.raises(ValueError):
        auth_mock._find_credentials()


def test_find_credentials_cfg_file(auth_mock):
    auth_mock.project_id = None
    auth_mock.project_api_key = None

    fp = Path(__file__).resolve().parent / "mock_data" / "test_config.json"
    auth_mock.cfg_file = fp

    auth_mock._find_credentials()
    assert auth_mock.project_id is not None
    assert auth_mock.project_api_key is not None


def test_endpoint(auth_mock):
    assert auth_mock._endpoint() == "https://api.up42.com"

    auth_mock.env = "abc"
    assert auth_mock._endpoint() == "https://api.up42.abc"


def test_get_token(auth_mock):
    auth_mock._get_token()
    assert auth_mock.token == TOKEN


@pytest.mark.live
def test_get_token_raises_wrong_credentials_live(auth_live):
    auth_live.project_id = "123"
    with pytest.raises(ValueError) as e:
        auth_live._get_token()
    assert (
        "Authentication was not successful, check the provided project credentials."
        in str(e.value)
    )


@pytest.mark.live
def test_get_token_live(auth_live):
    assert hasattr(auth_live, "token")


def test_get_workspace(auth_mock):
    auth_mock._get_workspace()
    assert auth_mock.workspace_id == WORKSPACE_ID


@pytest.mark.live
def test_get_workspace_live(auth_live):
    assert hasattr(auth_live, "workspace_id")


def test_generate_headers(auth_mock):
    version = io.open(
        Path(__file__).resolve().parents[1] / "up42/_version.txt", encoding="utf-8"
    ).read()
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token_1011",
        "cache-control": "no-cache",
        "X-UP42-info": f"python/{version}",
    }
    assert auth_mock._generate_headers(token="token_1011") == expected_headers


def test_request_helper(auth_mock, requests_mock):
    requests_mock.get(url="http://test.com", json={"data": {"xyz": 789}, "error": {}})

    response = auth_mock._request_helper(
        request_type="GET", url="http://test.com", data={}, querystring={}
    )
    response_json = json.loads(response.text)
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request(auth_mock, requests_mock):
    requests_mock.get(url="http://test.com", json={"data": {"xyz": 789}, "error": {}})

    response_json = auth_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request_non200_raises(auth_mock, requests_mock):
    requests_mock.get(
        url="http://test.com",
        json={"data": {}, "error": {"code": 403, "message": "some 403 error message"}},
        status_code=403,
    )

    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock._request(request_type="GET", url="http://test.com")
    assert "some 403 error message!" in str(e.value)


def test_request_non200_raises_error_not_dict(auth_mock, requests_mock):
    requests_mock.get(
        url="http://test.com",
        json={"data": {}, "error": "Not found!"},
        status_code=403,
    )

    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock._request(request_type="GET", url="http://test.com")
    assert "Not found!" in str(e.value)


def test_request_with_retry(auth_mock, requests_mock):
    auth_mock.retry = True
    # Retry contains getting a new token, already mocked in fixture.

    requests_mock.get(url="http://test.com", json={"data": {"xyz": 789}, "error": {}})

    response_json = auth_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request_rate_limited(auth_mock, requests_mock):
    a = requests_mock.get(
        "http://test.com",
        [
            {
                "status_code": 429,
                "json": {
                    "data": {},
                    "error": {"code": 429, "message": "rate limited"},
                },
            },
            {"json": {"data": {"xyz": 789}, "error": {}}},
        ],
    )

    response_json = auth_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}
    assert a.call_count == 2
