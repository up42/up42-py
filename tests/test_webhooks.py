import dataclasses
import random
import string
import uuid
from typing import List, Optional
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42 import webhooks

from .fixtures import fixtures_globals as constants

WEBHOOK_ID = str(uuid.uuid4())
HOOKS_URL = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks"
HOOK_URL = f"{HOOKS_URL}/{WEBHOOK_ID}"


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth.session = requests.session()
        workspace_mock.id = constants.WORKSPACE_ID
        yield


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
        "id": WEBHOOK_ID,
    }


metadata = random_metadata()


@pytest.fixture(name="webhook")
def _webhook():
    return webhooks.Webhook(
        id=metadata["id"],
        secret=metadata.get("secret"),
        active=metadata["active"],
        url=metadata["url"],
        name=metadata["name"],
        events=metadata["events"],
        created_at=metadata.get("createdAt"),
        updated_at=metadata.get("updatedAt"),
    )


class TestWebhook:
    def test_should_get_webhook(self, requests_mock: req_mock.Mocker, webhook: webhooks.Webhook):
        requests_mock.get(url=HOOK_URL, json={"data": metadata})
        assert webhooks.Webhook.get(WEBHOOK_ID) == webhook

    def test_should_provide_info(self, webhook):
        info = metadata.copy()
        info["created_at"] = info.pop("createdAt")
        info["updated_at"] = info.pop("updatedAt")
        assert webhook.info == info

    def test_should_provide_webhook_id(self, webhook):
        assert webhook.webhook_id == WEBHOOK_ID

    def test_should_trigger_test_events(self, requests_mock: req_mock.Mocker, webhook: webhooks.Webhook):
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
    @pytest.mark.parametrize("active", [True, False, None])
    @pytest.mark.parametrize("secret", [random_alphanumeric(), None])
    def test_should_update(
        self,
        requests_mock: req_mock.Mocker,
        webhook,
        name: Optional[str],
        url: Optional[str],
        events: Optional[List[str]],
        active: Optional[bool],
        secret: Optional[str],
    ):
        updated_at = "new-updated-at"
        requests_mock.put(url=HOOK_URL, json={"data": {"updatedAt": updated_at}})
        updates = {
            "name": name or metadata["name"],
            "url": url or metadata["url"],
            "events": events or metadata["events"],
            "active": active if active is not None else metadata["active"],
            "secret": secret or metadata["secret"],
        }

        hook = dataclasses.replace(webhook)
        assert (
            hook.update(name=name, url=url, active=active, events=events, secret=secret)
            == hook
            == dataclasses.replace(
                webhook,
                name=updates["name"],
                url=updates["url"],
                active=updates["active"],
                events=updates["events"],
                secret=updates["secret"],
                updated_at=updated_at,
            )
        )
        assert requests_mock.last_request and requests_mock.last_request.json() == updates

    def test_should_delete(self, requests_mock: req_mock.Mocker, webhook: webhooks.Webhook):
        requests_mock.delete(url=HOOK_URL)
        webhook.delete()
        assert requests_mock.called

    def test_should_save_new(self, requests_mock: req_mock.Mocker, webhook: webhooks.Webhook):
        hook = dataclasses.replace(webhook, id=None, created_at=None, updated_at=None)
        requests_mock.post(
            HOOKS_URL,
            json={
                "data": {
                    "id": metadata["id"],
                    "createdAt": metadata["createdAt"],
                    "updatedAt": metadata["updatedAt"],
                }
            },
        )
        hook.save()
        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "name": metadata["name"],
            "url": metadata["url"],
            "events": metadata["events"],
            "active": metadata["active"],
            "secret": metadata["secret"],
        }

    def test_should_save(self, requests_mock: req_mock.Mocker, webhook):
        updates = {
            "name": "new-name",
            "url": "new-url",
            "events": ["new-event"],
            "secret": "new-secret",
            "active": False,
        }
        hook = dataclasses.replace(webhook, **updates)
        updated_at = "new-updated-at"
        requests_mock.put(HOOK_URL, json={"data": {"updatedAt": updated_at}})
        hook.save()
        assert hook == dataclasses.replace(webhook, updated_at=updated_at, **updates)
        assert requests_mock.last_request and requests_mock.last_request.json() == updates


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

    def test_should_get_webhooks(self, requests_mock: req_mock.Mocker, webhook: webhooks.Webhook):
        requests_mock.get(HOOKS_URL, json={"data": [metadata]})
        assert self.webhooks.get_webhooks() == [webhook]

    def test_should_get_webhooks_as_dict(self, requests_mock: req_mock.Mocker):
        requests_mock.get(HOOKS_URL, json={"data": [metadata]})
        assert self.webhooks.get_webhooks(return_json=True) == [metadata]

    @pytest.mark.parametrize("secret", [random_alphanumeric(), None])
    def test_should_create_webhook(
        self,
        requests_mock: req_mock.Mocker,
        webhook: webhooks.Webhook,
        secret: Optional[str],
    ):
        name = random_alphanumeric()
        url = random_alphanumeric()
        events = [random_alphanumeric()]
        active = random.choice([True, False])
        requests_mock.post(HOOKS_URL, json={"data": metadata})
        assert self.webhooks.create_webhook(
            name=name, url=url, events=events, active=active, secret=secret
        ) == dataclasses.replace(webhook, name=name, url=url, active=active, events=events, secret=secret)

        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "name": name,
            "url": url,
            "events": events,
            "active": active,
            "secret": secret,
        }
