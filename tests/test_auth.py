import json
from pathlib import Path

import pytest
import requests

from .context import Auth, AuthenticationError

# pylint: disable=unused-import
from .fixtures import PROJECT_APIKEY, PROJECT_ID, TOKEN, WORKSPACE_ID, auth_live, auth_live_account, auth_mock


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


def test_no_credentials_raises(auth_mock):
    auth_mock.credentials_id = None
    auth_mock.credentials_key = None
    with pytest.raises(ValueError):
        auth_mock._find_credentials()


def test_cfg_file_not_found(auth_mock):
    auth_mock.credentials_id = None
    auth_mock.credentials_key = None
    fp = Path(__file__).resolve().parent / "mock_data" / "test_config_fake.json"
    auth_mock.cfg_file = fp
    with pytest.raises(ValueError) as e:
        auth_mock._find_credentials()
    assert "Selected config file does not exist!" in str(e.value)


def test_find_credentials_cfg_file(auth_mock):
    auth_mock.credentials_id = None
    auth_mock.credentials_key = None

    fp = Path(__file__).resolve().parent / "mock_data" / "test_config.json"
    auth_mock.cfg_file = fp

    auth_mock._find_credentials()
    assert auth_mock.credentials_id is not None
    assert auth_mock.credentials_key is not None


def test_endpoint(auth_mock):
    assert auth_mock._endpoint() == "https://api.up42.com"

    auth_mock.env = "abc"
    assert auth_mock._endpoint() == "https://api.up42.abc"


def test_get_token(auth_mock):
    auth_mock._get_token()
    assert auth_mock.token == TOKEN


def test_repr_project():
    auth = Auth(
        credentials_id=PROJECT_ID,
        credentials_key=PROJECT_APIKEY,
        authenticate=False,
        env="dev",
    )
    assert repr(auth) == f"UP42ProjectAuth(project_id={PROJECT_ID} ,dev)"


def test_repr_account():
    auth = Auth(
        credentials_id=PROJECT_ID,
        credentials_key=PROJECT_APIKEY,
        authenticate=False,
        auth_type="account-based",
        env="dev",
    )
    assert repr(auth) == f"UP42UserAuth(user_id={PROJECT_ID} ,dev)"


@pytest.mark.live
def test_get_token_raises_wrong_credentials_live(auth_live):
    auth_live.credentials_id = "123"
    with pytest.raises(ValueError) as e:
        auth_live._get_token()
    assert (
        "Authentication was not successful, check the provided project credentials."
        in str(e.value)
    )


@pytest.mark.live
def test_get_token_account_live_fail(auth_live_account):
    auth_live_account.credentials_id = "123"
    with pytest.raises(AuthenticationError) as e:
        auth_live_account._get_token()
    assert "Check the provided credentials." in str(e.value)


@pytest.mark.live
def test_get_token_live(auth_live):
    assert hasattr(auth_live, "token")


def test_get_workspace(auth_mock):
    auth_mock._get_user_id()
    assert auth_mock.workspace_id == WORKSPACE_ID


@pytest.mark.live
def test_get_workspace_live(auth_live):
    assert hasattr(auth_live, "workspace_id")


def test_generate_headers(auth_mock):
    version = (
        Path(__file__)  # pylint: disable=no-member
        .resolve()
        .parents[1]
        .joinpath("up42/_version.txt")
        .read_text(encoding="utf-8")
    )
    assert (
        isinstance(version, str) and "\n" not in version
    ), "check integrity of your version file"
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token_1011",
        "cache-control": "no-cache",
        "User-Agent": f"up42-py/{version} (https://github.com/up42/up42-py)",
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
