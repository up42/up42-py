from up42 import webhooks
import requests_mock as req_mock
from .fixtures import fixtures_globals as constants

HOOK_URL = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks/{constants.WEBHOOK_ID}"

metadata = {
    "url": "url",
    "name": "name",
    "active": True,
    "events": ["job.status"],
    "secret": "secret",
    "createdAt": "yesterday",
    "updatedAt": "now",
}

class TestWebhook:
    def test_should_initialize(self, auth_mock):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert metadata["name"] in repr(webhook)
        assert str(metadata["active"]) in repr(webhook)
        assert constants.WEBHOOK_ID in repr(webhook)
    
    def test_should_initialize_existing_hook(self, auth_mock, requests_mock: req_mock.Matcher):
        requests_mock.get(url=HOOK_URL, json={"data": metadata})
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert webhook.info == metadata
        assert metadata["name"] in repr(webhook)
        assert str(metadata["active"]) in repr(webhook)
        assert constants.WEBHOOK_ID in repr(webhook)
    
    def test_should_refresh_info(self, auth_mock, requests_mock: req_mock.Matcher):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        new_metadata = {
            "url": "new-url",
            "name": "new-name",
            "active": False,
            "events": ["new.status"],
            "secret": "new-secret",
            "createdAt": "now",
            "updatedAt": "tomorrow",
        }
        requests_mock.get(url=HOOK_URL, json={"data": new_metadata})
        assert webhook.info == new_metadata
        assert new_metadata["name"] in repr(webhook)
        assert str(new_metadata["active"]) in repr(webhook)
        
    def test_should_trigger_test_events(self, auth_mock, requests_mock: req_mock.Matcher):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        url = f"{HOOK_URL}/tests"
        test_event = {
            "startedAt": "2022-06-20T04:33:48.770826Z",
            "testsRun": 2,
            "testsSucceeded": 0,
        }
        requests_mock.post(url=url, json={"data": test_event})
        assert webhook.trigger_test_events() == test_event

    
    def test_should_update(self, auth_mock, requests_mock: req_mock.Matcher):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        requests_mock.get(url=HOOK_URL, json={"data": metadata})
        requests_mock.put(url=HOOK_URL, json=constants.JSON_WEBHOOK)
        updated_webhook = webhook.update(name="test_info_webhook")
        assert isinstance(updated_webhook, webhooks.Webhook)
        assert "test_info_webhook" in repr(updated_webhook)
    
    def test_should_delete(self, auth_mock, requests_mock: req_mock.Matcher):
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID, metadata)
        url = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks/{constants.WEBHOOK_ID}"
        requests_mock.delete(url=url)
        webhook.delete()
        assert requests_mock.called
    


def test_get_webhook_events(webhooks_mock):
    webhook_events = webhooks_mock.get_webhook_events()
    assert isinstance(webhook_events, list)
    assert len(webhook_events)


def test_get_webhooks(webhooks_mock):
    hooks = webhooks_mock.get_webhooks()
    assert isinstance(hooks, list)
    assert isinstance(hooks[0], webhooks.Webhook)


def test_get_webhooks_return_json(webhooks_mock):
    hooks = webhooks_mock.get_webhooks(return_json=True)
    assert isinstance(hooks, list)
    assert isinstance(hooks[0], dict)


def test_create_webhook(webhooks_mock):
    new_webhook = webhooks_mock.create_webhook(
        name="test_info_webhook",
        url="https://test-webhook-creation.com",
        events=["job.status"],
    )
    assert "test_info_webhook" in repr(new_webhook)
