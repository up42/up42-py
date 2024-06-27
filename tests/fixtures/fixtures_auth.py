import pytest
import requests_mock as req_mock

from up42 import auth as up42_auth

from . import fixtures_globals as constants


@pytest.fixture
def auth_mock(requests_mock: req_mock.Mocker) -> up42_auth.Auth:
    token_payload = {
        "data": {"accessToken": constants.TOKEN},
        "access_token": constants.TOKEN,
        "expires_in": 5 * 60,
        "token_type": "bearer",
    }
    requests_mock.post(constants.TOKEN_ENDPOINT, json=token_payload)
    return up42_auth.Auth(username=constants.USER_EMAIL, password=constants.PASSWORD)
