import pytest

from up42 import main

from .fixtures import fixtures_globals as constants


def test_get_webhook_events(requests_mock, auth_mock):  # pylint: disable=unused-argument
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
def test_get_webhooks(webhooks_mock, return_json):
    webhooks = main.get_webhooks(return_json=return_json)
    expected = webhooks_mock.get_webhooks(return_json=return_json)
    if return_json:
        assert webhooks == expected
    else:
        for hook, expected_hook in zip(webhooks, expected):
            assert hook.webhook_id == expected_hook.webhook_id
            assert hook._info == expected_hook._info  # pylint: disable=protected-access


class TestWorkspace:
    @pytest.fixture(autouse=True)
    def setup_auth_mock(self, auth_mock):
        main.workspace.auth = auth_mock
        yield

    def test_authenticate_success(self, auth_mock):
        main.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert main.workspace.id == constants.WORKSPACE_ID
        assert main.workspace.auth.token == auth_mock.token

    def test_fails_auth_property_without_authentication(self):
        main.workspace.auth = None
        with pytest.raises(main.UserNotAuthenticated):
            _ = main.workspace.auth

    def test_get_credits_balance(self):
        balance = main.get_credits_balance()
        assert isinstance(balance, dict)
        assert "balance" in balance
