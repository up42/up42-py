import pytest
import requests_mock as req_mock

import up42.main
from up42 import auth as up42_auth

from . import fixtures_globals as constants


@pytest.fixture
def auth_mock(requests_mock: req_mock.Mocker) -> up42_auth.Auth:
    json_get_token = {
        "data": {"accessToken": constants.TOKEN},
        "access_token": constants.TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post("https://api.up42.com/oauth/token", json=json_get_token)
    requests_mock.get(
        url="https://api.up42.com/users/me",
        json={"data": {"id": constants.WORKSPACE_ID}},
    )
    # get_credits_balance
    url_get_credits_balance = f"{constants.API_HOST}/accounts/me/credits/balance"
    requests_mock.get(
        url=url_get_credits_balance,
        json=constants.JSON_BALANCE,
    )
    up42.main.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
    return up42.main.workspace.auth
