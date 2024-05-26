import dataclasses
from typing import List, Optional

import pytest
import requests
import requests_mock as req_mock

from up42 import webhooks

from .fixtures import fixtures_globals as constants

HOOKS_URL = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks"
HOOK_URL = f"{HOOKS_URL}/{constants.WEBHOOK_ID}"

webhooks.Webhook.session = requests.session()
webhook = webhooks.Webhook(
    workspace_id=constants.WORKSPACE_ID,
    url="url",
    name="name",
    events=["event1", "event2"],
    active=True,
    secret="secret",
    id=constants.WEBHOOK_ID,
    created_at="created_at",
    updated_at="updated_at",
)

metadata = {
    "workspace_id": constants.WORKSPACE_ID,
    "url": "url",
    "name": "name",
    "events": ["event1", "event2"],
    "active": True,
    "secret": "secret",
    "id": constants.WEBHOOK_ID,
    "createdAt": "created_at",
    "updatedAt": "updated_at",
}


class TestWebhook:
    def test_should_get_webhook(self, requests_mock):
        requests_mock.get(HOOK_URL, json={"data": metadata})
        assert webhooks.Webhook.get(constants.WEBHOOK_ID, constants.WORKSPACE_ID) == webhook

    def test_should_list_webhooks(self, requests_mock):
        requests_mock.get(HOOKS_URL, json={"data": [metadata]})
        assert webhooks.Webhook.all(constants.WORKSPACE_ID) == [webhook]

    def test_should_delete(self, requests_mock: req_mock.Mocker):
        # TODO: what is actual status code on delete?
        requests_mock.delete(HOOK_URL, status_code=202)
        webhook.delete()
        assert requests_mock.called_once

    def test_should_provide_webhook_id(self):
        assert webhook.webhook_id == webhook.id

    def test_should_provide_info(self):
        info = metadata.copy()
        info["created_at"] = info.pop("createdAt")
        info["updated_at"] = info.pop("updatedAt")
        assert webhook.info == info

    def test_should_get_webhook_events(self, requests_mock):
        url = f"{constants.API_HOST}/webhooks/events"
        events = ["some-event"]
        requests_mock.get(
            url=url,
            json={
                "data": events,
                "error": {},
            },
        )
        assert webhooks.Webhook.all_webhook_events() == events

    def test_should_trigger_test_events(self, requests_mock):
        url = f"{HOOK_URL}/tests"
        events = ["some-test-event"]
        requests_mock.post(
            url=url,
            json={
                "data": events,
                "error": {},
            },
        )
        assert webhook.trigger_test_events() == events

    def test_should_save_new(self, requests_mock):
        copy = dataclasses.replace(webhook, id=None, created_at=None, updated_at=None)
        # TODO: check request body
        requests_mock.post(HOOKS_URL, json={"data": metadata})
        copy.save()
        assert copy == webhook

    def test_should_save(self, requests_mock):
        updates = {
            "name": "new-name",
            "url": "new-url",
            "events": ["new-event"],
            "secret": "new-secret",
            "active": False,
        }
        copy = dataclasses.replace(webhook, **updates)
        updated_at = "new-updated-at"
        payload = {
            **metadata,
            "updatedAt": updated_at,
        }
        # TODO: check request body
        requests_mock.put(HOOK_URL, json=payload)
        copy.save()
        assert copy == dataclasses.replace(webhook, updated_at=updated_at, **updates)

    def test_should_create(self, requests_mock):
        # TODO: check request body
        requests_mock.post(HOOKS_URL, json={"data": metadata})
        created = webhooks.Webhook.create(
            name=webhook.name,
            url=webhook.url,
            events=webhook.events,
            workspace_id=webhook.workspace_id,
            active=webhook.active,
            secret=webhook.secret,
        )
        assert created == webhook

    @pytest.mark.parametrize("name", ["new-name", None])
    @pytest.mark.parametrize("url", ["new-url", None])
    @pytest.mark.parametrize("events", [["new-event"], None])
    @pytest.mark.parametrize("secret", ["new-secret", None])
    @pytest.mark.parametrize("active", [False, None])
    def test_should_update(
        self,
        requests_mock,
        name: Optional[str],
        url: Optional[str],
        events: Optional[List[str]],
        secret: Optional[str],
        active: Optional[bool],
    ):
        copy = dataclasses.replace(webhook)
        updated_at = "new-updated-at"
        payload = {
            **metadata,
            "updatedAt": updated_at,
        }
        # TODO: check request body
        requests_mock.put(HOOK_URL, json=payload)

        assert (
            copy.update(name=name, url=url, events=events, secret=secret, active=active)
            == copy
            == dataclasses.replace(
                webhook,
                name=name or webhook.name,
                url=url or webhook.url,
                events=events or webhook.events,
                secret=secret or webhook.secret,
                active=active or webhook.active,
                updated_at=updated_at,
            )
        )
