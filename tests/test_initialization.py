from unittest import mock

import pytest

import up42
from up42 import catalog, main, storage, tasking

from .fixtures import fixtures_globals as constants


def test_fails_to_initialize_if_not_authenticated():
    with pytest.raises(main.UserNotAuthenticated):
        up42.initialize_catalog()
    with pytest.raises(main.UserNotAuthenticated):
        up42.initialize_storage()
    with pytest.raises(main.UserNotAuthenticated):
        up42.initialize_order(order_id=constants.ORDER_ID)
    with pytest.raises(main.UserNotAuthenticated):
        up42.initialize_asset(asset_id=constants.ASSET_ID)


def test_should_initialize_objects(
    auth_mock,
    order_mock,
    asset_mock,
):
    with mock.patch("up42.main.workspace") as workspace_mock:
        workspace_mock.id = constants.WORKSPACE_ID
        workspace_mock.auth = auth_mock

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
