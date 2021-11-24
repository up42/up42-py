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


def _mock_list_response_pages(total_pages, total_elements):
    def _one_page_reponse(page_nr, total_pages, total_elements):
        return {
            "data": {
                "content": [{"something1": 1}, {"something2": 2}, {"something3": 3}],
                "totalPages": total_pages,
                "totalElements": total_elements,
                "number": page_nr,
            },
        }

    return [
        {"json": _one_page_reponse(page_nr, total_pages, total_elements)}
        for page_nr in range(0, total_pages)
    ]


def test_paginate(storage_mock, requests_mock):
    url = "http://some_url/assets"

    limit = None
    size = 3
    total_pages = 4
    total_elements = 12
    expected = 12
    mock_list_response_pages = _mock_list_response_pages(total_pages, total_elements)
    requests_mock.get(url + f"&size={size}", mock_list_response_pages)
    res = storage_mock._query_paginated(url=url, limit=limit, size=size)
    assert len(res) == expected


def test_paginate_with_limit(storage_mock, requests_mock):
    """
    Test pagination with smaller limit than pagination size, and smaller limit than available elements.
    """
    url = "http://some_url/assets"

    limit = 5
    size = 50
    total_pages = 4
    total_elements = 12
    expected = 5
    mock_list_response_pages = _mock_list_response_pages(total_pages, total_elements)
    requests_mock.get(url + f"&size={limit}", mock_list_response_pages)
    res = storage_mock._query_paginated(url=url, limit=limit, size=size)
    assert len(res) == expected


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
