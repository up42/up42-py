import uuid

import mock

import up42
from tests import constants
from up42 import storage


def test_should_initialize_objects():
    storage_obj = up42.initialize_storage()
    assert isinstance(storage_obj, storage.Storage)
    assert storage_obj.workspace_id == constants.WORKSPACE_ID

    with mock.patch("up42.order.Order.get") as get_order:
        get_order.return_value = mock.sentinel
        assert up42.initialize_order(order_id=constants.ORDER_ID) == mock.sentinel
        get_order.assert_called_with(constants.ORDER_ID)

    asset_id = str(uuid.uuid4())
    with mock.patch("up42.asset.Asset.get") as get_asset:
        get_asset.return_value = mock.sentinel
        assert up42.initialize_asset(asset_id=asset_id) == mock.sentinel
        get_asset.assert_called_with(asset_id)
