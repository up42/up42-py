from up42 import webhooks

from .fixtures import fixtures_globals as constants

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
    
    def test_should_initialize_existing_hook(self, requests_mock):
        url = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks/{constants.WEBHOOK_ID}"
        requests_mock.post(url=url_create_webhook, json={"data": metadata})
        webhook = webhooks.Webhook(auth_mock, constants.WORKSPACE_ID, constants.WEBHOOK_ID)
        assert webhook.auth == auth_mock
        assert webhook.workspace_id == constants.WORKSPACE_ID
        assert webhook.webhook_id == constants.WEBHOOK_ID
        assert webhook.info == metadata
        assert metadata["name"] in repr(webhook)
        assert str(metadata["active"]) in repr(webhook)
        assert constants.WEBHOOK_ID in repr(webhook)

    
    def test_should_refresh_info(self):
        pass

    def test_should_trigger_test_events(self):
        pass
    
    def test_should_update(self):
        pass
    
    def test_should_delete(self):
        pass


def test_webhook_info(webhook_mock):
    info = webhook_mock.info
    assert info and info["id"] == constants.WEBHOOK_ID


def test_webhook_trigger_test_event(webhook_mock):
    test_event_info = webhook_mock.trigger_test_events()
    assert isinstance(test_event_info, dict)
    assert test_event_info["testsRun"] >= 1


def test_webhook_update(webhook_mock):
    updated_webhook = webhook_mock.update(name="test_info_webhook")
    assert isinstance(updated_webhook, webhooks.Webhook)
    assert "test_info_webhook" in repr(updated_webhook)


def test_webhook_delete(webhook_mock):
    webhook_mock.delete()


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
