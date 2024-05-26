import random
import string
from typing import List, Optional

import pytest
import requests_mock as req_mock

from up42 import webhooks

from .fixtures import fixtures_globals as constants

HOOK_URL = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks/{constants.WEBHOOK_ID}"


def random_alphanumeric():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


def random_metadata() -> dict:
    return {
        "url": random_alphanumeric(),
        "name": random_alphanumeric(),
        "active": random.choice([True, False]),
        "events": [random_alphanumeric()],
        "secret": random_alphanumeric(),
        "createdAt": random_alphanumeric(),
        "updatedAt": random_alphanumeric(),
    }


metadata = random_metadata()


class TestWebhook:
    def test_should_initialize(self, auth_mock):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert repr(webhook) == repr({**metadata, "id": constants.WEBHOOK_ID})

    def test_should_initialize_existing_hook(self, auth_mock, requests_mock: req_mock.Mocker):
        requests_mock.get(url=HOOK_URL, json={"data": metadata})
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert webhook.info == metadata
        assert repr(webhook) == repr({**metadata, "id": constants.WEBHOOK_ID})

    def test_should_refresh_info(
        self,
        auth_mock,
        requests_mock: req_mock.Mocker,
    ):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        new_metadata = random_metadata()
        requests_mock.get(url=HOOK_URL, json={"data": new_metadata})
        assert webhook.info == new_metadata
        assert repr(webhook) == repr({**new_metadata, "id": constants.WEBHOOK_ID})

    def test_should_trigger_test_events(self, auth_mock, requests_mock: req_mock.Mocker):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        url = f"{HOOK_URL}/tests"
        test_event = {
            "startedAt": "2022-06-20T04:33:48.770826Z",
            "testsRun": 2,
            "testsSucceeded": 0,
        }
        requests_mock.post(url=url, json={"data": test_event})
        assert webhook.trigger_test_events() == test_event

    @pytest.mark.parametrize("name", [random_alphanumeric(), None])
    @pytest.mark.parametrize("url", [random_alphanumeric(), None])
    @pytest.mark.parametrize("events", [[random_alphanumeric()], None])
    @pytest.mark.parametrize("active", [random.choice([True, False]), None])
    @pytest.mark.parametrize("secret", [random_alphanumeric(), None])
    def test_should_update(
        self,
        auth_mock,
        requests_mock: req_mock.Mocker,
        name: Optional[str],
        url: Optional[str],
        events: Optional[List[str]],
        active: Optional[bool],
        secret: Optional[str],
    ):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        latest_metadata = random_metadata()
        new_metadata = random_metadata()
        requests_mock.get(url=HOOK_URL, json={"data": latest_metadata})
        requests_mock.put(url=HOOK_URL, json={"data": new_metadata})
        updated_webhook = webhook.update(name=name, url=url, active=active, events=events, secret=secret)
        assert repr(updated_webhook) == repr({**new_metadata, "id": constants.WEBHOOK_ID})
        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "name": name or latest_metadata["name"],
            "url": url or latest_metadata["url"],
            "events": events or latest_metadata["events"],
            "active": active if active is not None else latest_metadata["active"],
            "secret": secret or latest_metadata["secret"],
        }

    def test_should_delete(self, auth_mock, requests_mock: req_mock.Mocker):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        requests_mock.delete(url=HOOK_URL)
        webhook.delete()
        assert requests_mock.called


class TestWebhooks:
    def test_get_webhook_events(self, webhooks_mock):
        webhook_events = webhooks_mock.get_webhook_events()
        assert isinstance(webhook_events, list)
        assert len(webhook_events)

    def test_get_webhooks(self, webhooks_mock):
        hooks = webhooks_mock.get_webhooks()
        assert isinstance(hooks, list)
        assert isinstance(hooks[0], webhooks.Webhook)

    def test_get_webhooks_return_json(self, webhooks_mock):
        hooks = webhooks_mock.get_webhooks(return_json=True)
        assert isinstance(hooks, list)
        assert isinstance(hooks[0], dict)

    def test_create_webhook(self, webhooks_mock):
        new_webhook = webhooks_mock.create_webhook(
            name="test_info_webhook",
            url="https://test-webhook-creation.com",
            events=["job.status"],
        )
        assert "test_info_webhook" in repr(new_webhook)
