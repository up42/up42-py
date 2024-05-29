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

    def test_get_webhook_events(self, requests_mock):
        url_webhook_events = f"{constants.API_HOST}/webhooks/events"
        events = ["some-event"]
        requests_mock.get(
            url=url_webhook_events,
            json={
                "data": events,
                "error": {},
            },
        )
        assert base.get_webhook_events() == events

    @pytest.mark.parametrize("return_json", [False, True])
    def test_get_webhooks(self, webhooks_mock, return_json):
        webhooks = base.get_webhooks(return_json=return_json)
        expected = webhooks_mock.get_webhooks(return_json=return_json)
        if return_json:
            assert webhooks == expected
        else:
            for hook, expected_hook in zip(webhooks, expected):
                assert hook.webhook_id == expected_hook.webhook_id
                assert hook._info == expected_hook._info  # pylint: disable=protected-access

    def test_get_credits_balance(self, requests_mock):
        balance_url = f"{constants.API_HOST}/accounts/me/credits/balance"
        balance = {"balance": 10693}
        requests_mock.get(
            url=balance_url,
            json={"data": balance},
        )
        assert base.get_credits_balance() == balance


class TestSession:
    @pytest.fixture(autouse=True)
    def workspace(self, auth_mock):
        with mock.patch("up42.base.workspace") as workspace_mock:
            workspace_mock.auth = auth_mock
            workspace_mock.id = constants.WORKSPACE_ID
            yield

    @pytest.fixture
    def record(self):
        class ActiveRecord:
            session = base.Session()

        return ActiveRecord()

    def test_should_provide_session_if_authenticated(self, record):
        assert record.session == base.workspace.auth.session


class TestWorkspaceId:
    @pytest.fixture(autouse=True)
    def workspace(self, auth_mock):
        with mock.patch("up42.base.workspace") as workspace_mock:
            workspace_mock.auth = auth_mock
            workspace_mock.id = constants.WORKSPACE_ID
            yield

    class ActiveRecord:
        workspace_id = base.WorkspaceId()

        def __init__(self, workspace_id=None):
            if workspace_id:
                self.workspace_id = workspace_id

    @pytest.fixture
    def record_set_value(self):
        return self.ActiveRecord(workspace_id="custom_workspace_id")

    @pytest.fixture
    def record_not_set_value(self):
        return self.ActiveRecord()

    def test_should_provided_local_if_set_workspace(self, record_set_value):
        assert record_set_value.workspace_id == "custom_workspace_id"

    def test_should_provide_workspace_id_if_not_provided_authenticated(self, record_not_set_value):
        assert record_not_set_value.workspace_id == constants.WORKSPACE_ID
