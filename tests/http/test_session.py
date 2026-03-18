import random
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42 import constants
from up42.http import session as up42_session

SOME_URL = "https://something.com"

METHODS_WITH_CALLS = [
    ("GET", requests.Session.get),
    ("POST", requests.Session.post),
    ("PUT", requests.Session.put),
    ("PATCH", requests.Session.patch),
    ("DELETE", requests.Session.delete),
    ("OPTIONS", requests.Session.options),
    ("HEAD", requests.Session.head),
]

AUTHORIZATION_VALUE = "Bearer some-token"
SDK_VERSION = "some-version"
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": AUTHORIZATION_VALUE,
    "cache-control": "no-cache",
    "User-Agent": f"up42-py/{SDK_VERSION} ({constants.REPOSITORY_URL})",
}


def set_token(request: requests.Request):
    request.headers["Authorization"] = AUTHORIZATION_VALUE
    return request


@pytest.fixture(name="auth_session")
def create_session():
    auth = mock.MagicMock(side_effect=set_token)
    create_adapter = mock.MagicMock(
        return_value=requests.adapters.HTTPAdapter()
    )
    return up42_session.create(
        auth=auth, create_adapter=create_adapter, version=SDK_VERSION
    )


@pytest.mark.parametrize("method, call", METHODS_WITH_CALLS)
def test_should_respond_on_good_status(
    requests_mock: req_mock.Mocker, auth_session, method, call
):
    status_code = random.randint(200, 399)
    requests_mock.request(
        method,
        SOME_URL,
        request_headers=REQUEST_HEADERS,
        status_code=status_code,
    )
    assert call(auth_session, SOME_URL).status_code == status_code
    assert requests_mock.called_once


@pytest.mark.parametrize("method, call", METHODS_WITH_CALLS)
def test_fails_on_bad_status(
    requests_mock: req_mock.Mocker, auth_session, method, call
):
    body = '{"type": "https://docs.up42.com/problems/eula-not-accepted", "title": "EULA not accepted"}'
    status_code = random.randint(400, 599)
    requests_mock.request(
        method,
        SOME_URL,
        request_headers=REQUEST_HEADERS,
        status_code=status_code,
        text=body,
    )
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        call(auth_session, SOME_URL)

    http_error = exc_info.value
    error_message = str(http_error)

    assert http_error.response is not None
    assert http_error.response.status_code == status_code
    assert "Response body:" in error_message
    assert "eula-not-accepted" in error_message
    assert "EULA not accepted" in error_message
    assert requests_mock.called_once


def test_http_error_skips_body_when_response_not_json(
    requests_mock: req_mock.Mocker, auth_session
):
    requests_mock.get(
        SOME_URL,
        request_headers=REQUEST_HEADERS,
        status_code=500,
        text="<html>Internal Server Error</html>",
    )
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        auth_session.get(SOME_URL)

    http_error = exc_info.value
    error_message = str(http_error)
    assert http_error.response.status_code == 500
    assert "Response body:" not in error_message
    assert "500 Server Error" in error_message
    assert requests_mock.called_once
