import datetime as dt
import random
import urllib
from typing import Optional, cast

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import asset, order, storage, utils


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
        requests_mock: req_mock.Mocker,
        order_metadata: dict,
    ):
        sortby: storage.OrderSortBy = "status"
        order_type: storage.OrderType = random.choice(["TASKING", "ARCHIVE"])
        tags = ["some", "tags"]
        name = "name"
        workspace_params = {"workspaceId": constants.WORKSPACE_ID} if workspace_orders else {}
        status = [status.value for status in statuses] if statuses else None
        status_params = {"status": status} if status else {}
        query = urllib.parse.urlencode(
            {
                "sort": utils.SortingField(sortby, not descending),
                **workspace_params,
                "displayName": name,
                "type": order_type,
                "tags": tags,
                **status_params,
                "page": 0,
            },
            doseq=True,
        )
        expected = [order_metadata] * 20
        requests_mock.get(
            f"{constants.API_HOST}/v2/orders?{query}",
            json={"content": expected, "page": 0, "totalPages": 1},
        )
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
        if return_json:
            assert orders == expected[:limit]
        else:
            assert orders == [order.Order.from_dict(info) for info in expected[:limit]]
