# pylint: disable=unused-import
from .context import Webhooks
from .fixtures import (
    webhooks_mock,
    webhooks_live,
    auth_mock,
    auth_live,
)


def test_get_webhook_events(webhooks_mock):
    webhook_events = webhooks_mock.get_webhook_events()
    assert isinstance(webhook_events, list)


def test_get_webhook_events_live(webhooks_live):
    webhook_events = webhooks_live.get_webhook_events()
    assert isinstance(webhook_events, list)


def test_get_webhooks(webhooks_mock):
    webhooks = webhooks_mock.get_webhooks()
    assert isinstance(webhooks, list)


def test_get_webhooks_live(webhooks_live):
    webhooks = webhooks_live.get_webhooks()
    assert isinstance(webhooks, list)
