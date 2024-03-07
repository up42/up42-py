import os

import pytest

from up42.auth import Auth

from . import fixtures_globals as constants


@pytest.fixture(name="auth_project_mock")
def _auth_project_mock(requests_mock):
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
    auth = Auth(project_id=constants.PROJECT_ID, project_api_key=constants.PROJECT_APIKEY, authenticate=True)

    # get_blocks
    url_get_blocks = f"{constants.API_HOST}/blocks"
    requests_mock.get(
        url=url_get_blocks,
        json=constants.JSON_BLOCKS,
    )
    # get_credits_balance
    url_get_credits_balance = f"{constants.API_HOST}/accounts/me/credits/balance"
    requests_mock.get(
        url=url_get_credits_balance,
        json=constants.JSON_BALANCE,
    )

    return auth


@pytest.fixture(name="auth_account_mock")
def _auth_account_mock(requests_mock):
    json_get_token = {
        "data": {"accessToken": constants.TOKEN},
        "access_token": constants.TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post("https://api.up42.com/oauth/token", json=json_get_token)
    requests_mock.get(url="https://api.up42.com/users/me", json={"data": {"id": constants.WORKSPACE_ID}})
    return Auth(username="user@up42.com", password="password", authenticate=True)


@pytest.fixture(name="auth_mock", params=["project", "account"])
def _auth_mock(request, auth_project_mock, auth_account_mock):
    mocks = {"project": auth_project_mock, "account": auth_account_mock}
    return mocks[request.param]


@pytest.fixture(name="project_id_live")
def _project_id_live():
    return os.getenv("TEST_UP42_PROJECT_ID")


@pytest.fixture(name="project_api_key_live")
def _project_api_key_live():
    return os.getenv("TEST_UP42_PROJECT_API_KEY")


@pytest.fixture(name="username_test_live")
def _username_test_live():
    return os.getenv("TEST_USERNAME")


@pytest.fixture(name="password_test_live")
def _password_test_live():
    return os.getenv("TEST_PASSWORD")


@pytest.fixture(name="auth_live", params=["project", "account"])
def _auth_live(request, auth_project_live, auth_account_live):
    mocks = {"project": auth_project_live, "account": auth_account_live}
    return mocks[request.param]
