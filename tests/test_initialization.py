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
