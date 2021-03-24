import pytest

# pylint: disable=unused-import
from .context import Storage, Asset, Order
from .fixtures import (
    ASSET_ID,
    ORDER_ID,
    WORKSPACE_ID,
    auth_mock,
    auth_live,
    storage_mock,
    storage_live,
)


def test_init(storage_mock):
    assert isinstance(storage_mock, Storage)
    assert storage_mock.workspace_id == WORKSPACE_ID


def test_paginate(storage_mock, requests_mock):
    url = "http://some_url/assets"

    def paginated_response(page):
        return {
            "data": {
                "content": [{"something": "is"}, {"something": "is_not"}],
                "totalPages": 3,
                "totalElements": 6,
                "number": page,
            },
        }

    requests_mock.get(
        "/assets", [{"json": paginated_response(page)} for page in range(0, 3)]
    )
    res = storage_mock._paginate(url)
    assert len(res) == 6


def test_get_assets(storage_mock):
    assets = storage_mock.get_assets()
    assert len(assets) == 1
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == ASSET_ID


@pytest.mark.live
def test_get_assets_live(storage_live):
    assets = storage_live.get_assets()
    assert len(assets) >= 2


def test_get_orders(storage_mock):
    orders = storage_mock.get_orders()
    assert len(orders) == 1
    assert isinstance(orders[0], Order)
    assert orders[0].order_id == ORDER_ID


@pytest.mark.live
def test_get_orders_live(storage_live):
    orders = storage_live.get_orders()
    assert len(orders) >= 1
