import pytest

from up42 import main

from .fixtures import fixtures_globals as constants


def test_get_credits_balance(auth_mock):  # pylint: disable=unused-argument
    main.workspace.auth = auth_mock
    balance = main.get_credits_balance()
    assert isinstance(balance, dict)
    assert "balance" in balance


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
    def test_fails_to_get_auth_safely_if_workspace_not_authenticated(self):
        main.workspace.auth = None
        with pytest.raises(main.UserNotAuthenticated):
            _ = main.workspace.auth
