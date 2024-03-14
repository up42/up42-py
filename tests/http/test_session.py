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


def set_token(request: requests.Request):
    request.headers["Authorization"] = AUTHORIZATION_VALUE
    return request


@pytest.fixture(name="auth_session")
def create_session():
    create_auth = mock.MagicMock(return_value=mock.MagicMock(side_effect=set_token))
    create_adapter = mock.MagicMock(return_value=requests.adapters.HTTPAdapter())
    session = up42_session.create(create_adapter=create_adapter, create_auth=create_auth)
    yield session
    create_auth.assert_called_with(create_adapter=create_adapter)


@pytest.mark.parametrize("method, call", METHODS_WITH_CALLS)
def test_should_respond_on_good_status(requests_mock: req_mock.Mocker, auth_session, method, call):
    status_code = random.randint(200, 400)
    requests_mock.request(
        method, SOME_URL, request_headers={"Authorization": AUTHORIZATION_VALUE}, status_code=status_code
    )
    assert call(auth_session, SOME_URL).status_code == status_code
    assert requests_mock.called_once


@pytest.mark.parametrize("method, call", METHODS_WITH_CALLS)
def test_fails_on_bad_status(requests_mock: req_mock.Mocker, auth_session, method, call):
    status_code = random.randint(400, 599)
    requests_mock.request(
        method, SOME_URL, request_headers={"Authorization": AUTHORIZATION_VALUE}, status_code=status_code
    )
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        call(auth_session, SOME_URL)
    response = exc_info.value.response
    assert response is not None and response.status_code == status_code
    assert requests_mock.called_once
