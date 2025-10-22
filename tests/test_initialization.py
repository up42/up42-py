import mock

import up42
from tests import constants


def test_should_initialize_objects():
    with mock.patch("up42.order.Order.get") as get_order:
        get_order.return_value = mock.sentinel
        assert up42.initialize_order(order_id=constants.ORDER_ID) == mock.sentinel
        get_order.assert_called_with(constants.ORDER_ID)
