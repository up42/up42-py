import datetime as dt
import random
import urllib
from typing import Optional, cast

import mock
import pytest
import requests_mock as req_mock

from tests import constants
from up42 import asset, storage, utils


class TestStorage:
    @pytest.mark.parametrize("limit", [10, None])
    @pytest.mark.parametrize("descending", [False, True])
    @pytest.mark.parametrize("return_json", [False, True])
    def test_should_get_assets(
        self,
        limit: Optional[int],
        descending: bool,
        return_json: bool,
        requests_mock: req_mock.Mocker,
    ):
        created_after = dt.datetime.now() - dt.timedelta(days=1)
        created_before = dt.datetime.now() + dt.timedelta(days=1)
        collection_names = ["collection", "names"]
        producer_names = ["producer", "names"]
        tags = ["producer", "names"]
        sources = ["some", "sources"]
        search = "search"
        sortby = "updatedAt"
        query = urllib.parse.urlencode(
            {
                "createdAfter": utils.format_time(created_after),
                "createdBefore": utils.format_time(created_before),
                "workspaceId": constants.WORKSPACE_ID,
                "collectionNames": collection_names,
                "producerNames": producer_names,
                "tags": tags,
                "sources": sources,
                "search": search,
                "sort": utils.SortingField(sortby, not descending),
                "page": 0,
            },
            doseq=True,
        )
        expected = [{"asset": "info"}] * 20
        requests_mock.get(
            f"{constants.API_HOST}/v2/assets?{query}",
            json={"content": expected, "page": 0, "totalPages": 1},
        )
        assets = storage.Storage().get_assets(
            created_after=created_after,
            created_before=created_before,
            workspace_id=constants.WORKSPACE_ID,
            collection_names=collection_names,
            producer_names=producer_names,
            tags=tags,
            sources=sources,
            search=search,
            limit=limit,
            sortby=sortby,
            descending=descending,
            return_json=return_json,
        )
        if return_json:
            assert assets == expected[:limit]
        else:
            assert [cast(asset.Asset, asset_obj).info for asset_obj in assets] == expected[:limit]

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
            if return_json:
                order_obj = mock.MagicMock()
                order_obj.info = mock.sentinel
                get_orders.return_value = iter([order_obj] * 20)
            else:
                get_orders.return_value = iter([mock.sentinel] * 20)
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
            assert orders == ([mock.sentinel] * 20)[:limit]
            get_orders.assert_called_with(
                workspace_id=constants.WORKSPACE_ID if workspace_orders else None,
                display_name=name,
                order_type=order_type,
                tags=tags,
                status=status,  # type: ignore
                sort_by=utils.SortingField(sortby, not descending),
            )
