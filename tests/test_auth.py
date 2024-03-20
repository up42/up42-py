import pathlib
from typing import cast

import pytest
import requests
import requests_mock as req_mock

from up42 import auth as up42_auth
from up42 import utils

from .fixtures import fixtures_globals as constants


def test_auth_kwargs():
    auth = up42_auth.Auth(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
        authenticate=False,
    )
    assert not auth.token


def test_no_credentials_raises():
    with pytest.raises(ValueError):
        up42_auth.Auth()


def test_should_fail_config_file_not_found(tmp_path):
    config_path = tmp_path / "config_fake.json"
    with pytest.raises(ValueError) as e:
        up42_auth.Auth(cfg_file=config_path)
    assert str(config_path) in str(e.value)


def test_should_not_authenticate_with_config_file_if_not_requested():
    fp = pathlib.Path(__file__).resolve().parent / "mock_data" / "test_config.json"
    up42_auth.Auth(cfg_file=fp, authenticate=False)


def test_get_workspace(auth_mock: up42_auth.Auth):
    assert auth_mock.workspace_id == constants.WORKSPACE_ID


def test_should_set_headers(auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
    expected_code = 207
    test_url = "http://test.com"
    version = utils.get_up42_py_version()
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {constants.TOKEN}",
        "cache-control": "no-cache",
        "User-Agent": f"up42-py/{version} (https://github.com/up42/up42-py)",
    }
    requests_mock.get(test_url, request_headers=expected_headers, status_code=expected_code)
    response = cast(requests.Response, auth_mock.request("GET", test_url, return_text=False))
    assert response.status_code == expected_code
    assert requests_mock.called


def test_request(auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
    requests_mock.get(url="http://test.com", json={"data": {"xyz": 789}, "error": {}})

    response_json = auth_mock.request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request_non200_raises(auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
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


def test_request_non200_raises_error_not_dict(auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
    requests_mock.get(
        url="http://test.com",
        json={"data": {}, "error": "Not found!"},
        status_code=403,
    )

    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock.request(request_type="GET", url="http://test.com")
    assert "Not found!" in str(e.value)


def test_request_non200_raises_error_apiv2(auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
    """
    Errors that are raised in the http response with the api v2 format
    """
    requests_mock.get(
        url="http://test.com",
        json={"title": "Bad request", "status": 400},
        status_code=400,
    )
    with pytest.raises(requests.exceptions.RequestException) as e:
        auth_mock.request(request_type="GET", url="http://test.com")
        assert "title" in str(e.value)


def test_request_200_raises_error_apiv2(auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
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
