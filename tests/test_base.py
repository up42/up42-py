import dataclasses
import unittest
from typing import Union
from unittest import mock

import pytest

from up42 import base

from .fixtures import fixtures_globals as constants


class TestWorkspace:
    def test_fails_to_provide_properties_if_not_authenticated(self):
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.auth
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.id

    def test_should_authenticate(self, requests_mock):
        requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
        requests_mock.get(
            url="https://api.up42.com/users/me",
            json={"data": {"id": constants.WORKSPACE_ID}},
        )
        base.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert base.workspace.id == constants.WORKSPACE_ID


# TODO: these tests to be moved to test_initialization
class TestNonWorkspace:
    @pytest.fixture(autouse=True)
    def workspace(self, auth_mock):
        with mock.patch("up42.base.workspace") as workspace_mock:
            workspace_mock.auth = auth_mock
            workspace_mock.id = constants.WORKSPACE_ID
            yield

    @unittest.mock.patch("up42.webhooks.Webhooks")
    def test_should_get_webhook_events(self, webhooks: mock.MagicMock, auth_mock):
        events = mock.MagicMock()
        webhooks.return_value.get_webhook_events.return_value = events
        assert base.get_webhook_events() == events
        webhooks.assert_called_with(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)

    @unittest.mock.patch("up42.webhooks.Webhooks")
    @pytest.mark.parametrize("return_json", [False, True])
    def test_should_get_webhooks(self, webhooks: mock.MagicMock, auth_mock, return_json):
        hooks = mock.MagicMock()
        webhooks.return_value.get_webhooks.return_value = hooks
        assert base.get_webhooks(return_json=return_json) == hooks
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
        assert webhook == base.create_webhook(name, url, events, active, secret)
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
        assert base.get_credits_balance() == balance


@dataclasses.dataclass(eq=True)
class ActiveRecord:
    session = base.Session()
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


class TestDescriptors:
    @pytest.fixture(autouse=True)
    def workspace(self, auth_mock):
        with mock.patch("up42.base.workspace") as workspace_mock:
            workspace_mock.auth = auth_mock
            workspace_mock.id = constants.WORKSPACE_ID
            yield

    def test_should_provide_session(self):
        record = ActiveRecord()
        assert record.session == base.workspace.auth.session

    def test_session_should_not_be_represented(self):
        assert "session" not in repr(ActiveRecord())

    def test_should_allow_to_set_workspace_id(self):
        record = ActiveRecord(workspace_id="custom_workspace_id")
        assert record.workspace_id == "custom_workspace_id"
        assert "custom_workspace_id" in repr(record)

    def test_should_provide_default_workspace_id(self):
        record = ActiveRecord()
        assert record.workspace_id == constants.WORKSPACE_ID
        assert constants.WORKSPACE_ID in repr(record)
