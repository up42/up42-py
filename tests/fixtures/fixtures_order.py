import json
import os
from pathlib import Path

import pytest

from ..context import Order
from .fixtures_globals import ORDER_ID


@pytest.fixture()
def order_mock(auth_mock, requests_mock):
    # order info
    url_order_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/{ORDER_ID}"
    )

    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/order_data/archive_order_info.json",
        encoding="utf-8",
    ) as json_file:
        json_oder_schenma = json.load(json_file)
        requests_mock.get(url=url_order_info, json=json_oder_schenma)

    order = Order(auth=auth_mock, order_id=ORDER_ID)

    return order


@pytest.fixture()
def order_live(auth_live):
    order = Order(auth=auth_live, order_id=os.getenv("TEST_UP42_ORDER_ID"))
    return order
