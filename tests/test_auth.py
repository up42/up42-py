import pathlib
from typing import cast

import pytest
import requests
from requests_mock import Mocker

from up42 import host, utils
from up42.auth import Auth

from .fixtures import fixtures_globals as constants


def test_auth_kwargs():
    auth = Auth(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
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


def test_should_fail_config_file_not_found(tmp_path):
    config_path = tmp_path / "config_fake.json"
    with pytest.raises(ValueError) as e:
        Auth(cfg_file=config_path)
    assert str(config_path) in str(e.value)


def test_should_not_authenticate_with_config_file_if_not_requested():
    fp = pathlib.Path(__file__).resolve().parent / "mock_data" / "test_config.json"
    Auth(cfg_file=fp, authenticate=False)


def test_should_set_api_host_domain_with_environment(auth_mock):
    auth_mock.env = "abc"
    assert host.DOMAIN == "abc"


def test_get_token(auth_mock, requests_mock: Mocker):
    expected_code = 207
    version = utils.get_up42_py_version()
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {constants.TOKEN}",
        "cache-control": "no-cache",
        "User-Agent": f"up42-py/{version} (https://github.com/up42/up42-py)",
    }
    requests_mock.get("http://test.com", request_headers=expected_headers, status_code=expected_code)
    response = cast(requests.Response, auth_mock.request("GET", "http://test.com", return_text=False))
    assert response.status_code == expected_code
    assert requests_mock.called


def test_request(auth_mock, requests_mock):
    requests_mock.get(url="http://test.com", json={"data": {"xyz": 789}, "error": {}})

    response_json = auth_mock.request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request_non200_raises(auth_mock, requests_mock):
    requests_mock.get(
        url="http://test.com",
        json={
            "data": {},
            "error": {"code": 403, "message": "some 403 error message"},
        },
        status_code=403,
    )

    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock.request(request_type="GET", url="http://test.com")
    assert "{'code': 403, 'message': 'some 403 error message'}" in str(e.value)


def test_request_non200_raises_error_not_dict(auth_mock, requests_mock):
    requests_mock.get(
        url="http://test.com",
        json={"data": {}, "error": "Not found!"},
        status_code=403,
    )

    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock.request(request_type="GET", url="http://test.com")
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
        auth_mock.request(request_type="GET", url="http://test.com")
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
        auth_mock.request(request_type="GET", url="http://test.com")
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
        auth_mock.request(request_type="GET", url="http://test.com")
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

    response_json = auth_mock.request(request_type="GET", url="http://test.com")
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

    response_json = auth_mock.request(request_type="GET", url="http://test.com")
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

    response_json = auth_mock.request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}
    assert a.call_count == 4
