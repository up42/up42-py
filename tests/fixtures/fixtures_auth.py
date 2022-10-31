import os

import pytest

from .fixtures_globals import (
    TOKEN,
    PROJECT_ID,
    WORKSPACE_ID,
    PROJECT_APIKEY,
    JSON_BLOCKS,
    JSON_BALANCE,
)
from ..context import Auth, main


@pytest.fixture()
def auth_mock(requests_mock):
    # token for initial authentication
    url_get_token = "https://api.up42.com/oauth/token"
    json_get_token = {
        "data": {"accessToken": TOKEN},
        "access_token": TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post(url_get_token, json=json_get_token)

    url_get_workspace = f"https://api.up42.com/projects/{PROJECT_ID}"
    json_get_workspace = {"data": {"workspaceId": WORKSPACE_ID}}
    requests_mock.get(
        url=url_get_workspace,
        json=json_get_workspace,
    )
    auth = Auth(
        project_id=PROJECT_ID, project_api_key=PROJECT_APIKEY, authenticate=True
    )

    # get_blocks
    url_get_blocks = f"{auth._endpoint()}/blocks"
    requests_mock.get(
        url=url_get_blocks,
        json=JSON_BLOCKS,
    )

    # get_credits_balance
    url_get_credits_balance = f"{auth._endpoint()}/accounts/me/credits/balance"
    requests_mock.get(
        url=url_get_credits_balance,
        json=JSON_BALANCE,
    )

    return auth


@pytest.fixture(scope="module")
def auth_live():
    auth = Auth(
        project_id=os.getenv("TEST_UP42_PROJECT_ID"),
        project_api_key=os.getenv("TEST_UP42_PROJECT_API_KEY"),
    )
    main._auth = auth  # instead of authenticate()
    return auth
