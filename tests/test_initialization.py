from unittest import mock

import pytest
import requests_mock as req_mock

import up42
from up42 import catalog, host, order, storage, tasking

from .fixtures import fixtures_globals as constants


@pytest.fixture(autouse=True)
def workspace(auth_mock):
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth = auth_mock
        workspace_mock.id = constants.WORKSPACE_ID
        yield


def test_should_initialize_objects(requests_mock: req_mock.Mocker, order_mock: order.Order):
    catalog_obj = up42.initialize_catalog()
    assert isinstance(catalog_obj, catalog.Catalog)

    storage_obj = up42.initialize_storage()
    assert isinstance(storage_obj, storage.Storage)
    assert storage_obj.workspace_id == constants.WORKSPACE_ID

    order_obj = up42.initialize_order(order_id=constants.ORDER_ID)
    assert order_obj.info == order_mock.info

    url = host.endpoint(f"/v2/assets/{constants.ASSET_ID}/metadata")
    asset_info = {"id": constants.ASSET_ID, "other": "data"}
    requests_mock.get(url=url, json=asset_info)
    asset_obj = up42.initialize_asset(asset_id=constants.ASSET_ID)
    assert asset_obj.info == asset_info

    result = up42.initialize_tasking()
    assert isinstance(result, tasking.Tasking)
