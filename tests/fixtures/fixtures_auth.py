import pytest
import requests_mock as req_mock

from up42 import auth as up42_auth

from . import fixtures_globals as constants


@pytest.fixture
def auth_mock(requests_mock: req_mock.Mocker) -> up42_auth.Auth:
    token_payload = {
        "data": {"accessToken": constants.TOKEN},
        "access_token": constants.TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post("https://api.up42.com/oauth/token", json=token_payload)
    return up42_auth.Auth(username=constants.USER_EMAIL, password=constants.PASSWORD)
