import random
from typing import Optional

import mock
import pytest

from tests import constants
from up42 import storage, utils

SENTINELS = [mock.sentinel] * 20


def mock_items(get_items: mock.MagicMock, return_json: bool):
    if return_json:
        item = mock.MagicMock()
        item.info = mock.sentinel
        get_items.return_value = iter([item] * 20)
    else:
        get_items.return_value = iter(SENTINELS)


class TestStorage:
    @pytest.mark.parametrize("limit", [10, None])
    @pytest.mark.parametrize("descending", [False, True])
    @pytest.mark.parametrize("workspace_orders", [False, True])
    @pytest.mark.parametrize("return_json", [False, True])
    @pytest.mark.parametrize("statuses", [None, random.choices(list(storage.AllowedStatuses), k=3)])
    def test_should_get_orders(
        self,
        limit: Optional[int],
        descending: bool,
        workspace_orders: bool,
        return_json: bool,
        statuses: Optional[list[storage.AllowedStatuses]],
    ):
        sortby: storage.OrderSortBy = "status"
        order_type: storage.OrderType = random.choice(["TASKING", "ARCHIVE"])
        tags = ["some", "tags"]
        name = "name"
        status = [status.value for status in statuses] if statuses else None
        with mock.patch("up42.order.Order.all") as get_orders:
            mock_items(get_orders, return_json)
            orders = storage.Storage().get_orders(
                workspace_orders=workspace_orders,
                return_json=return_json,
                limit=limit,
                sortby=sortby,
                descending=descending,
                order_type=order_type,
                statuses=status,
                name=name,
                tags=tags,
            )
            assert orders == SENTINELS[:limit]
            get_orders.assert_called_with(
                workspace_id=constants.WORKSPACE_ID if workspace_orders else None,
                display_name=name,
                order_type=order_type,
                tags=tags,
                status=status,  # type: ignore
                sort_by=utils.SortingField(sortby, not descending),
            )
