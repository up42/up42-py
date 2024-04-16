import pytest

from up42 import main

from .fixtures import fixtures_globals as constants


@pytest.fixture(autouse=True)
def setup_auth_mock(auth_mock):
    main._auth = auth_mock  # pylint: disable=protected-access
    yield


def test_get_credits_balance():
    balance = main.get_credits_balance()
    assert isinstance(balance, dict)
    assert "balance" in balance


def test_fails_to_get_auth_safely_if_unauthenticated():
    main._auth = None  # pylint: disable=protected-access
    with pytest.raises(ValueError):
        main.get_auth_safely()


def test_get_webhook_events(requests_mock):
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
