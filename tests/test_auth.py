import json
from pathlib import Path

import pytest
import requests

from up42 import host
from up42.auth import Auth
from up42.utils import get_up42_py_version

from .fixtures.fixtures_globals import PROJECT_APIKEY, PROJECT_ID, TOKEN, WORKSPACE_ID


def test_auth_kwargs():
    auth = Auth(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        env="abc",
        authenticate=False,
        retry=False,
    )
    assert auth.env == "abc"
    assert host.DOMAIN == "abc"
    assert not auth.authenticate


def test_no_credentials_raises():
    with pytest.raises(ValueError):
        Auth()


def test_cfg_file_not_found():
    fp = Path(__file__).resolve().parent / "mock_data" / "test_config_fake.json"
    with pytest.raises(ValueError) as e:
        Auth(cfg_file=fp)
    assert "Selected config file does not exist!" in str(e.value)


def test_should_not_authenticate_with_config_file_if_not_requested():
    fp = Path(__file__).resolve().parent / "mock_data" / "test_config.json"
    Auth(cfg_file=fp, authenticate=False)


def test_should_set_api_host_domain_with_environment(auth_mock):
    auth_mock.env = "abc"
    assert host.DOMAIN == "abc"


def test_get_token(auth_mock):
    auth_mock._get_token()
    assert auth_mock.token == TOKEN


@pytest.mark.live
def test_get_token_raises_wrong_credentials_live(auth_live):
    auth_live._credentials_id = "123"
    with pytest.raises(ValueError) as e:
        auth_live._get_token()
    assert "Authentication" in str(e.value)


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
    version = get_up42_py_version()
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token_1011",
        "cache-control": "no-cache",
        "User-Agent": f"up42-py/{version} (https://github.com/up42/up42-py)",
    }
    assert auth_mock._generate_headers(token="token_1011") == expected_headers


def test_request_helper(auth_mock, requests_mock):
    requests_mock.get(url="http://test.com", json={"data": {"xyz": 789}, "error": {}})

    response = auth_mock._request_helper(request_type="GET", url="http://test.com", data={}, querystring={})
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
    assert "{'code': 403, 'message': 'some 403 error message'}" in str(e.value)


def test_request_non200_raises_error_not_dict(auth_mock, requests_mock):
    requests_mock.get(
        url="http://test.com",
        json={"data": {}, "error": "Not found!"},
        status_code=403,
    )

    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock._request(request_type="GET", url="http://test.com")
    assert "Not found!" in str(e.value)


def test_request_non200_raises_error_apiv2(auth_mock, requests_mock):
    """
    Errors that are raised in the http response with the api v2 format
    Live tests are included in the specific tests classes.
    e.g. test_storage (test_get_assets_raise_error_live)
    """
    requests_mock.get(
        url="http://test.com",
        json={"title": "Bad request", "status": 400},
        status_code=400,
    )
    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock._request(request_type="GET", url="http://test.com")
        assert "title" in str(e.value)


def test_request_200_raises_error_apiv2(auth_mock, requests_mock):
    """
    Errors that are raised in a positive the http response
    and included in the error key
    """
    requests_mock.get(
        url="http://test.com",
        json={
            "data": None,
            "error": "Some default error not related to Http",
        },
        status_code=200,
    )
    with pytest.raises(ValueError) as e:
        auth_mock._request(request_type="GET", url="http://test.com")
        assert "error" in str(e.value)


def test_request_token_still_timed_out_after_retry_raises(auth_mock, requests_mock):
    a = requests_mock.get(
        "http://test.com",
        [
            {
                "status_code": 401,
                "json": {
                    "data": {},
                    "error": {"code": 401, "message": "token timeout"},
                },
            },
            {
                "status_code": 401,
                "json": {
                    "data": {},
                    "error": {"code": 401, "message": "token timeout"},
                },
            },
            {"json": {"data": {"xyz": 789}, "error": {}}},
        ],
    )

    with pytest.raises(requests.exceptions.RequestException):
        auth_mock._request(request_type="GET", url="http://test.com")
    assert a.call_count == 2


def test_request_token_timed_out_retry(auth_mock, requests_mock):
    a = requests_mock.get(
        "http://test.com",
        [
            {
                "status_code": 401,
                "json": {
                    "data": {},
                    "error": {"code": 401, "message": "token timeout"},
                },
            },
            {"json": {"data": {"xyz": 789}, "error": {}}},
        ],
    )

    response_json = auth_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}
    assert a.call_count == 2


def test_request_rate_limited_retry(auth_mock, requests_mock):
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


def test_request_token_timeout_during_rate_limitation(auth_mock, requests_mock):
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
            {
                "status_code": 401,
                "json": {
                    "data": {},
                    "error": {"code": 401, "message": "token timeout"},
                },
            },
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
    assert a.call_count == 4
