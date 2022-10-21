import os

import pytest

from .fixtures_globals import WEBHOOK_ID, JSON_WEBHOOK

from ..context import (
    Webhook,
    Webhooks,
)


@pytest.fixture()
def webhook_mock(auth_mock, requests_mock):
    # webhook info
    url_webhook_info = f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/webhooks/{WEBHOOK_ID}"
    requests_mock.get(url=url_webhook_info, json=JSON_WEBHOOK)

    # test event
    url_test_event = f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/webhooks/{WEBHOOK_ID}/tests"
    json_test_event = {
        "data": {
            "startedAt": "2022-06-20T04:33:48.770826Z",
            "testsRun": 2,
            "testsSucceeded": 0,
        }
    }
    requests_mock.post(url=url_test_event, json=json_test_event)

    # update
    url_update = f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/webhooks/{WEBHOOK_ID}"
    requests_mock.put(url=url_update, json=JSON_WEBHOOK)

    # delete
    url_delete = f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/webhooks/{WEBHOOK_ID}"
    requests_mock.delete(url=url_delete)

    return Webhook(auth=auth_mock, webhook_id=WEBHOOK_ID)


@pytest.fixture()
def webhook_live(auth_live):
    return Webhook(auth=auth_live, webhook_id=os.getenv("TEST_UP42_WEBHOOK_ID"))


@pytest.fixture()
def webhooks_mock(auth_mock, requests_mock):
    # events
    url_events = f"{auth_mock._endpoint()}/webhooks/events"
    events_json = {"data": [{"name": "job.status"}], "error": None}
    requests_mock.get(url=url_events, json=events_json)

    # get webhooks
    url_webhooks = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/webhooks"
    )
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
    url_create_webhook = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/webhooks"
    )
    requests_mock.post(url=url_create_webhook, json=JSON_WEBHOOK)

    return Webhooks(auth=auth_mock)


@pytest.fixture()
def webhooks_live(auth_live):
    return Webhooks(auth=auth_live)
