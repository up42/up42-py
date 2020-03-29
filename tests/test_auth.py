import json
from pathlib import Path

import pytest
import requests_mock

from .fixtures import auth_mock_no_request, auth_mock


def test_no_credentials_raises(auth_mock_no_request):
    auth_mock_no_request.project_id = None
    auth_mock_no_request.project_api_key = None
    with pytest.raises(ValueError):
        auth_mock_no_request._find_credentials()


def test_find_credentials_cfg_file(auth_mock_no_request):
    auth_mock_no_request.project_id = None
    auth_mock_no_request.project_api_key = None

    fp = Path(__file__).parent / "mock_data" / "test_config.json"
    auth_mock_no_request.cfg_file = fp

    auth_mock_no_request._find_credentials()
    assert auth_mock_no_request.project_id is not None
    assert auth_mock_no_request.project_api_key is not None


def test_endpoint(auth_mock_no_request):
    assert auth_mock_no_request._endpoint() == "https://api.up42.com"

    auth_mock_no_request.env = "abc"
    assert auth_mock_no_request._endpoint() == "https://api.up42.abc"


def test_get_token_project(auth_mock_no_request):
    with requests_mock.Mocker() as m:
        url_token = f"https://{auth_mock_no_request.project_id}:{auth_mock_no_request.project_api_key}@api.up42.{auth_mock_no_request.env}/oauth/token"
        m.post(
            url=url_token, text='{"data":{"accessToken":"token_789"}}',
        )
        auth_mock_no_request._get_token_project()
    assert auth_mock_no_request.token == "token_789"


def test_generate_headers(auth_mock_no_request):
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer token_1011",
        "cache-control": "no-cache",
    }
    assert (
        auth_mock_no_request._generate_headers(token="token_1011") == expected_headers
    )


def test_request_helper(auth_mock):
    with requests_mock.Mocker() as m:
        m.get(url="http://test.com", text='{"data": {"xyz":789}, "error":{}}')

        response = auth_mock._request_helper(
            request_type="GET", url="http://test.com", data={}, querystring={}
        )
    response_json = json.loads(response.text)
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request(auth_mock):
    with requests_mock.Mocker() as m:
        m.get(url="http://test.com", text='{"data": {"xyz":789}, "error":{}}')

        response_json = auth_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request_with_retry(auth_mock):
    auth_mock.retry = True
    with requests_mock.Mocker() as m:
        # Retry contains getting a new token, needs to be mocked separately.
        url_token = f"https://{auth_mock.project_id}:{auth_mock.project_api_key}@api.up42.{auth_mock.env}/oauth/token"
        m.post(
            url=url_token, text='{"data":{"accessToken":"token_123"}}',
        )

        m.get(url="http://test.com", text='{"data": {"xyz":789}, "error":{}}')

        response_json = auth_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}
