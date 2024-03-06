import random
from unittest import mock

import pytest
import requests
from requests import adapters
from requests_mock import Mocker

from up42.http import session as up42_session

some_url = "https://something.com"

methods_and_calls = [
    ("GET", requests.Session.get),
    ("POST", requests.Session.post),
    ("PUT", requests.Session.put),
    ("PATCH", requests.Session.patch),
    ("DELETE", requests.Session.delete),
    ("OPTIONS", requests.Session.options),
    ("HEAD", requests.Session.head),
]

authorization_value = "Bearer some-token"


def set_token(request: requests.Request):
    request.headers["Authorization"] = authorization_value
    return request


create_auth = mock.MagicMock(return_value=mock.MagicMock(side_effect=set_token))
create_adapter = mock.MagicMock(return_value=adapters.HTTPAdapter())


@pytest.fixture(name="auth_session")
def create_session():
    session = up42_session.create(create_adapter=create_adapter, create_auth=create_auth)
    yield session
    create_auth.assert_called_with(create_adapter=create_adapter)


@pytest.mark.parametrize("method, call", methods_and_calls)
def test_should_respond_on_good_status(requests_mock: Mocker, auth_session, method, call):
    status_code = random.randint(200, 400)
    requests_mock.request(
        method, some_url, request_headers={"Authorization": authorization_value}, status_code=status_code
    )
    assert call(auth_session, some_url).status_code == status_code
    assert requests_mock.called_once


@pytest.mark.parametrize("method, call", methods_and_calls)
def test_fails_on_bad_status(requests_mock: Mocker, auth_session, method, call):
    status_code = random.randint(400, 600)
    requests_mock.request(
        method, some_url, request_headers={"Authorization": authorization_value}, status_code=status_code
    )
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        call(auth_session, some_url)
    response = exc_info.value.response
    assert response is not None and response.status_code == status_code
    assert requests_mock.called_once
