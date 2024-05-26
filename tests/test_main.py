import unittest
from unittest import mock

import pytest

from up42 import main

from .fixtures import fixtures_globals as constants


class TestWorkspace:
    def test_fails_to_provide_properties_if_not_authenticated(self):
        with pytest.raises(main.UserNotAuthenticated):
            _ = main.workspace.auth
        with pytest.raises(main.UserNotAuthenticated):
            _ = main.workspace.id

    def test_should_authenticate(self, requests_mock):
        requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
        requests_mock.get(
            url="https://api.up42.com/users/me",
            json={"data": {"id": constants.WORKSPACE_ID}},
        )
        main.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert main.workspace.id == constants.WORKSPACE_ID


# TODO: these tests to be moved to test_initialization
class TestNonWorkspace:
    @pytest.fixture(autouse=True)
    def workspace(self, auth_mock):
        with mock.patch("up42.main.workspace") as workspace_mock:
            workspace_mock.auth = auth_mock
            workspace_mock.id = constants.WORKSPACE_ID
            yield

    @unittest.mock.patch("up42.webhooks.Webhooks")
    def test_should_get_webhook_events(self, webhooks: mock.MagicMock, auth_mock):
        events = mock.MagicMock()
        webhooks.return_value.get_webhook_events.return_value = events
        assert main.get_webhook_events() == events
        webhooks.assert_called_with(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)

    @unittest.mock.patch("up42.webhooks.Webhooks")
    @pytest.mark.parametrize("return_json", [False, True])
    def test_should_get_webhooks(self, webhooks: mock.MagicMock, auth_mock, return_json):
        hooks = mock.MagicMock()
        webhooks.return_value.get_webhooks.return_value = hooks
        assert main.get_webhooks(return_json=return_json) == hooks
        webhooks.assert_called_with(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
        webhooks.return_value.get_webhooks.assert_called_with(return_json=return_json)

    @unittest.mock.patch("up42.webhooks.Webhooks")
    def test_should_create_webhook(self, webhooks: mock.MagicMock, auth_mock):
        name = "name"
        url = "url"
        events = ["event"]
        active = True
        secret = "secret"
        webhook = mock.MagicMock()
        webhooks.return_value.create_webhook.return_value = webhook
        assert webhook == main.create_webhook(name, url, events, active, secret)
        webhooks.assert_called_with(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
        webhooks.return_value.create_webhook.assert_called_with(
            name=name, url=url, events=events, active=active, secret=secret
        )

    def test_should_get_credits_balance(self, requests_mock):
        balance_url = f"{constants.API_HOST}/accounts/me/credits/balance"
        balance = {"balance": 10693}
        requests_mock.get(
            url=balance_url,
            json={"data": balance},
        )
        assert main.get_credits_balance() == balance
