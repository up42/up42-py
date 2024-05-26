import random
import string
from typing import List, Optional

import pytest
import requests_mock as req_mock

from up42 import webhooks

from .fixtures import fixtures_globals as constants

HOOKS_URL = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks"
HOOK_URL = f"{HOOKS_URL}/{constants.WEBHOOK_ID}"


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
        "id": constants.WEBHOOK_ID,
    }


metadata = random_metadata()


class TestWebhook:
    def test_should_initialize(self, auth_mock):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert repr(webhook) == repr(metadata)

    def test_should_initialize_existing_hook(self, auth_mock, requests_mock: req_mock.Mocker):
        requests_mock.get(url=HOOK_URL, json={"data": metadata})
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert webhook.info == metadata
        assert repr(webhook) == repr(metadata)

    def test_should_refresh_info(
        self,
        auth_mock,
        requests_mock: req_mock.Mocker,
    ):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        new_metadata = random_metadata()
        requests_mock.get(url=HOOK_URL, json={"data": new_metadata})
        assert webhook.info == new_metadata
        assert repr(webhook) == repr(new_metadata)

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
        assert repr(updated_webhook) == repr(new_metadata)
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
    @pytest.fixture(autouse=True)
    def setup_webhooks(self, auth_mock):
        self.webhooks = webhooks.Webhooks(auth_mock, constants.WORKSPACE_ID)

    def test_should_get_webhook_events(self, requests_mock: req_mock.Mocker):
        url = f"{constants.API_HOST}/webhooks/events"
        events = ["some-event"]
        requests_mock.get(
            url=url,
            json={
                "data": events,
                "error": {},
            },
        )
        assert self.webhooks.get_webhook_events() == events

    def test_should_get_webhooks(self, requests_mock: req_mock.Mocker):
        requests_mock.get(HOOKS_URL, json={"data": [metadata]})
        (webhook,) = self.webhooks.get_webhooks()
        assert isinstance(webhook, webhooks.Webhook)
        assert webhook.auth == self.webhooks.auth
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert repr(webhook) == repr(metadata)

    def test_get_webhooks_as_dict(self, requests_mock: req_mock.Mocker):
        hook = {**metadata, "id": constants.WEBHOOK_ID}
        requests_mock.get(HOOKS_URL, json={"data": [hook]})
        assert self.webhooks.get_webhooks(return_json=True) == [hook]

    @pytest.mark.parametrize("secret", [random_alphanumeric(), None])
    def test_should_create_webhook(
        self,
        requests_mock: req_mock.Mocker,
        secret: Optional[str],
    ):
        name = random_alphanumeric()
        url = random_alphanumeric()
        events = [random_alphanumeric()]
        active = random.choice([True, False])
        requests_mock.post(HOOKS_URL, json={"data": metadata})
        webhook = self.webhooks.create_webhook(name=name, url=url, events=events, active=active, secret=secret)
        assert webhook.auth == self.webhooks.auth
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert repr(webhook) == repr(metadata)
        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "name": name,
            "url": url,
            "events": events,
            "active": active,
            "secret": secret,
        }
