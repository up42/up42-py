import pytest

# pylint: disable=unused-import
from .context import Webhook
from .fixtures import WEBHOOK_ID, WORKSPACE_ID


def test_webhook_initiate(webhook_mock):
    assert isinstance(webhook_mock, Webhook)
    assert webhook_mock.webhook_id == WEBHOOK_ID
    assert webhook_mock.workspace_id == WORKSPACE_ID


def test_webhook_info(webhook_mock):
    assert webhook_mock.info
    assert webhook_mock._info["id"] == WEBHOOK_ID


def test_webhook_trigger_test_event(webhook_mock):
    test_event_info = webhook_mock.trigger_test_events()
    assert isinstance(test_event_info, dict)
    assert test_event_info["testsRun"] >= 1


def test_webhook_update(webhook_mock):
    updated_webhook = webhook_mock.update(name="test_info_webhook")
    assert isinstance(updated_webhook, Webhook)
    assert updated_webhook._info["name"] == "test_info_webhook"


def test_webhook_delete(webhook_mock):
    webhook_mock.delete()


def test_get_webhook_events(webhooks_mock):
    webhook_events = webhooks_mock.get_webhook_events()
    assert isinstance(webhook_events, list)
    assert len(webhook_events)


@pytest.mark.live
def test_get_webhook_events_live(webhooks_live):
    webhook_events = webhooks_live.get_webhook_events()
    assert isinstance(webhook_events, list)
    assert len(webhook_events)


def test_get_webhooks(webhooks_mock):
    webhooks = webhooks_mock.get_webhooks()
    assert isinstance(webhooks, list)
    assert isinstance(webhooks[0], Webhook)


def test_get_webhooks_return_json(webhooks_mock):
    webhooks = webhooks_mock.get_webhooks(return_json=True)
    assert isinstance(webhooks, list)
    assert isinstance(webhooks[0], dict)


@pytest.mark.live
def test_get_webhooks_live(webhooks_live):
    webhooks = webhooks_live.get_webhooks()
    assert isinstance(webhooks, list)
    assert len(webhooks) == 3  # TEST_UP42_WEBHOOK_ID env variable needs to be updated
    # assert isinstance(webhooks[0], Webhook)


def test_create_webhook(webhooks_mock):
    new_webhook = webhooks_mock.create_webhook(
        name="test_info_webhook",
        url="https://test-webhook-creation.com",
        events=["job.status"],
    )
    assert new_webhook._info["name"] == "test_info_webhook"


@pytest.mark.live
def test_create_webhook_live(webhooks_live):
    new_webhook = webhooks_live.create_webhook(
        name="test_webhook_creation",
        url="https://test-webhook-creation.com",
        events=["job.status"],
    )
    assert new_webhook._info["name"] == "test_webhook_creation"
    new_webhook.delete()
