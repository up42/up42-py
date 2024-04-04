import random
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

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
    "User-Agent": f"up42-py/{SDK_VERSION} ({up42_session.REPOSITORY_URL})",
}


def set_token(request: requests.Request):
    request.headers["Authorization"] = AUTHORIZATION_VALUE
    return request


@pytest.fixture(name="auth_session")
def create_session():
    auth = mock.MagicMock(side_effect=set_token)
    create_adapter = mock.MagicMock(return_value=requests.adapters.HTTPAdapter())
    return up42_session.create(auth=auth, create_adapter=create_adapter, version=SDK_VERSION)


@pytest.mark.parametrize("method, call", METHODS_WITH_CALLS)
def test_should_respond_on_good_status(requests_mock: req_mock.Mocker, auth_session, method, call):
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
def test_fails_on_bad_status(requests_mock: req_mock.Mocker, auth_session, method, call):
    status_code = random.randint(400, 599)
    requests_mock.request(
        method,
        SOME_URL,
        request_headers=REQUEST_HEADERS,
        status_code=status_code,
    )
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        call(auth_session, SOME_URL)
    response = exc_info.value.response
    assert response is not None and response.status_code == status_code
    assert requests_mock.called_once
