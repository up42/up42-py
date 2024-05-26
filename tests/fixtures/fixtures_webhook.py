import pytest

from up42 import webhooks

from . import fixtures_globals as constants


@pytest.fixture
def webhooks_mock(auth_mock, requests_mock):
    # get webhooks
    url_webhooks = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks"
    webhooks_json = {
        "data": [
            {
                "url": "a.com",
                "name": "a",
                "active": True,
                "events": ["job.status"],
                "id": "123",
                "secret": "foobar2k",
                "createdAt": "2022-04-13T19:19:19.357571Z",
                "updatedAt": "2022-04-13T19:19:19.357571Z",
            },
            {
                "url": "b.com",
                "name": "b",
                "active": True,
                "events": ["order.status"],
                "id": "d6971221-846c-48a1-bb0d-c00d49a4ba70",
                "secret": "foobar2k",
                "createdAt": "2022-04-13T19:19:40.68348Z",
                "updatedAt": "2022-04-13T19:19:40.68348Z",
            },
        ],
        "error": None,
    }
    requests_mock.get(url=url_webhooks, json=webhooks_json)

    # create webhook
    url_create_webhook = f"{constants.API_HOST}/workspaces/{constants.WORKSPACE_ID}/webhooks"
    requests_mock.post(url=url_create_webhook, json=constants.JSON_WEBHOOK)

    return webhooks.Webhooks(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
