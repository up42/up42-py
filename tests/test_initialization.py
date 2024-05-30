from unittest import mock

import pytest

import up42
from up42 import catalog, storage, tasking

from .fixtures import fixtures_globals as constants


@pytest.fixture(autouse=True)
def workspace(auth_mock):
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth = auth_mock
        workspace_mock.id = constants.WORKSPACE_ID
        yield


@pytest.fixture(name="webhooks")
def _webhooks():
    with mock.patch("up42.webhooks.Webhook") as webhooks_class_mock:
        yield webhooks_class_mock


def test_should_initialize_objects(
    order_mock,
    asset_mock,
):
    catalog_obj = up42.initialize_catalog()
    assert isinstance(catalog_obj, catalog.Catalog)

    storage_obj = up42.initialize_storage()
    assert isinstance(storage_obj, storage.Storage)
    assert storage_obj.workspace_id == constants.WORKSPACE_ID

    order_obj = up42.initialize_order(order_id=constants.ORDER_ID)
    assert order_obj.info == order_mock.info
    asset_obj = up42.initialize_asset(asset_id=constants.ASSET_ID)
    assert asset_obj.info == asset_mock.info
    result = up42.initialize_tasking()
    assert isinstance(result, tasking.Tasking)


def test_should_get_webhook_events(webhooks: mock.MagicMock):
    events = mock.MagicMock()
    webhooks.get_webhook_events.return_value = events
    assert up42.get_webhook_events() == events


@pytest.mark.parametrize("return_json", [False, True])
def test_should_get_webhooks(webhooks: mock.MagicMock, return_json):
    hooks = mock.MagicMock()
    webhooks.all.return_value = hooks
    assert up42.get_webhooks(return_json=return_json) == hooks
    webhooks.all.assert_called_with(return_json=return_json)


def test_should_create_webhook(webhooks: mock.MagicMock):
    name = "name"
    url = "url"
    events = ["event"]
    active = True
    secret = "secret"
    webhook = mock.MagicMock()
    webhooks.create.return_value = webhook
    assert webhook == up42.create_webhook(name, url, events, active, secret)
    webhooks.create.assert_called_with(name=name, url=url, events=events, active=active, secret=secret)
