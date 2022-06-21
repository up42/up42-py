import os

import pytest

# pylint: disable=unused-import
from .context import Webhooks, Webhook
from .fixtures import (
    WEBHOOK_ID,
    WORKSPACE_ID,
    webhook_mock,
    webhooks_mock,
    webhook_live,
    webhooks_live,
    auth_mock,
    auth_live,
)


def test_webhook_initiate(webhook_mock):
    assert isinstance(webhook_mock, Webhook)
    assert webhook_mock.webhook_id == WEBHOOK_ID
    assert webhook_mock.workspace_id == WORKSPACE_ID


def test_webhook_info(webhook_mock):
    assert webhook_mock.info
    assert webhook_mock.info["id"] == WEBHOOK_ID


@pytest.mark.live
def test_webhook_info_live(webhook_live):
    assert webhook_live.info
    assert webhook_live.info["id"] == os.getenv("TEST_UP42_WEBHOOK_ID")


def test_webhook_trigger_test_event(webhook_mock):
    test_event_info = webhook_mock.trigger_test_events()
    assert isinstance(test_event_info, dict)
    assert test_event_info["testsRun"] > 1


@pytest.mark.live
def test_webhook_trigger_test_event_live(webhook_live):
    test_event_info = webhook_live.trigger_test_events()
    assert isinstance(test_event_info, dict)
    assert test_event_info["testsRun"] > 1


def test_webhook_update(webhook_mock):
    updated_info = webhook_mock.update(name="test_info_webhook")
    assert isinstance(updated_info, dict)
    assert webhook_mock._info["name"] == "test_info_webhook"


@pytest.mark.live
def test_webhook_update_live(webhook_live):
    updated_info = webhook_live.update(
        name="test_info_webhook"
    )  # "Updates" to the old name for consistency.
    assert isinstance(updated_info, dict)
    assert webhook_live._info["name"] == "test_info_webhook"


def test_webhook_delete(webhook_mock):
    webhook_mock.delete()


def test_get_webhook_events(webhooks_mock):
    webhook_events = webhooks_mock.get_webhook_events()
    assert isinstance(webhook_events, list)
    assert len(webhook_events)


# @pytest.mark.live
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
    assert len(webhooks)
    assert isinstance(webhooks[0], Webhook)
