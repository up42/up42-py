import os

import pytest

from .fixtures_globals import ORDER_ID, JSON_ORDER

from ..context import (
    Order,
)


@pytest.fixture()
def order_mock(auth_mock, requests_mock):
    # order info
    url_order_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/{ORDER_ID}"
    )
    requests_mock.get(url=url_order_info, json=JSON_ORDER)

    order = Order(auth=auth_mock, order_id=ORDER_ID)

    return order


@pytest.fixture()
def order_live(auth_live):
    order = Order(auth=auth_live, order_id=os.getenv("TEST_UP42_ORDER_ID"))
    return order
