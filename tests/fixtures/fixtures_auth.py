import os

import pytest

from ..context import Auth, main
from .fixtures_globals import JSON_BALANCE, JSON_BLOCKS, PROJECT_APIKEY, PROJECT_ID, TOKEN, WORKSPACE_ID


@pytest.fixture
def auth_project_mock(requests_mock):
    json_get_token = {
        "data": {"accessToken": TOKEN},
        "access_token": TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post("https://api.up42.com/oauth/token", json=json_get_token)
    requests_mock.get(
        url="https://api.up42.com/users/me",
        json={"data": {"id": WORKSPACE_ID}},
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


@pytest.fixture
def auth_account_mock(requests_mock):
    json_get_token = {
        "data": {"accessToken": TOKEN},
        "access_token": TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post("https://api.up42.com/oauth/token", json=json_get_token)
    requests_mock.get(
        url="https://api.up42.com/users/me", json={"data": {"id": WORKSPACE_ID}}
    )
    return Auth(username="user@up42.com", password="password", authenticate=True)


@pytest.fixture(params=["project", "account"])
def auth_mock(request, auth_project_mock, auth_account_mock):
    mocks = {"project": auth_project_mock, "account": auth_account_mock}
    return mocks[request.param]


@pytest.fixture(scope="module")
def project_id_live():
    return os.getenv("TEST_UP42_PROJECT_ID")


@pytest.fixture(scope="module")
def project_api_key_live():
    return os.getenv("TEST_UP42_PROJECT_API_KEY")


@pytest.fixture(scope="module")
def username_test_live():
    return os.getenv("TEST_USERNAME")


@pytest.fixture(scope="module")
def password_test_live():
    return os.getenv("TEST_PASSWORD")


@pytest.fixture(scope="module")
def auth_project_live(project_id_live, project_api_key_live):
    auth = Auth(project_id=project_id_live, project_api_key=project_api_key_live)
    main._auth = auth  # instead of authenticate()
    return auth


@pytest.fixture(scope="module")
def auth_account_live(username_test_live, password_test_live):
    auth = Auth(username=username_test_live, password=password_test_live)
    main._auth = auth  # instead of authenticate()
    return auth


@pytest.fixture(params=["project", "account"])
def auth_live(request, auth_project_live, auth_account_live):
    mocks = {"project": auth_project_live, "account": auth_account_live}
    return mocks[request.param]
