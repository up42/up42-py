from .context import Order
from .fixtures import (
    ORDER_ID,
    WORKSPACE_ID,
    auth_mock,
    auth_live,
    order_mock,
    order_live,
)


def test_init(order_mock):
    assert isinstance(order_mock, Order)
    assert order_mock.order_id == ORDER_ID
    assert order_mock.workspace_id == WORKSPACE_ID
