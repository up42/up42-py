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
