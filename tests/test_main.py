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
        main.workspace = main._Workspace()  # pylint: disable=protected-access

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
        assert main.get_webhook_events() == events

    @pytest.mark.parametrize("return_json", [False, True])
    def test_get_webhooks(self, webhooks_mock, return_json):
        webhooks = main.get_webhooks(return_json=return_json)
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
        assert main.get_credits_balance() == balance


class TestSession:
    @pytest.fixture(scope="function")
    def dummy_instance(self):
        class DummyInstance:
            session = main.Session()

        return DummyInstance()

    def test_should_fail_if_not_authenticated(self, dummy_instance):
        with pytest.raises(main.UserNotAuthenticated):
            _ = dummy_instance.session

    def test_should_provide_session_if_authenticated(self, requests_mock, dummy_instance):
        requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
        requests_mock.get(
            url="https://api.up42.com/users/me",
            json={"data": {"id": constants.WORKSPACE_ID}},
        )
        main.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert dummy_instance.session == main.workspace.auth.session


class TestWorkspaceId:
    @pytest.fixture
    def dummy_instance_without_local_id(self, requests_mock):
        requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
        requests_mock.get(
            url="https://api.up42.com/users/me",
            json={"data": {"id": constants.WORKSPACE_ID}},
        )
        main.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)

        class DummyInstance:
            workspace_id = main.WorkspaceId()

        yield DummyInstance()
        main.workspace = main._Workspace()  # pylint: disable=protected-access

    def test_should_provided_local_if_set_workspace(self):
        class DummyInstance:
            workspace_id = main.WorkspaceId()

            def __init__(self, workspace_id=None):
                if workspace_id:
                    self.__dict__["workspace_id"] = workspace_id

        instance_with_id = DummyInstance(workspace_id="custom_id")
        assert instance_with_id.workspace_id == "custom_id"

    def test_should_provide_workspace_id_if_not_provided_authenticated(self, dummy_instance_without_local_id):
        assert dummy_instance_without_local_id.workspace_id == constants.WORKSPACE_ID

    def test_should_fail_if_not_authenticated(self):
        class DummyInstance:
            workspace_id = main.WorkspaceId()

        instance_with_id = DummyInstance()
        with pytest.raises(main.UserNotAuthenticated):
            _ = instance_with_id.workspace_id
