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
    JSON_ASSET,
    JSON_ORDER,
)


def test_init(storage_mock):
    assert isinstance(storage_mock, Storage)
    assert storage_mock.workspace_id == WORKSPACE_ID


def _mock_one_page_reponse(page_nr, size, total_pages, total_elements):
    return {
        "data": {
            "content": [{"something1": 1}] * size,
            "totalPages": total_pages,
            "totalElements": total_elements,
            "number": page_nr,
        },
    }


def test_paginate_one_page(storage_mock, requests_mock):
    url = "http://some_url/assets"

    limit = None
    size = 50
    total_pages = 1
    total_elements = 30
    expected = 30
    requests_mock.get(
        url + f"&size={size}",
        json=_mock_one_page_reponse(0, expected, total_pages, total_elements),
    )
    res = storage_mock._query_paginated(url=url, limit=limit, size=size)
    assert len(res) == expected


def test_paginate_multiple_pages(storage_mock, requests_mock):
    url = "http://some_url/assets"

    limit = 20
    size = 3
    total_pages = 4
    total_elements = 12
    expected = 12
    requests_mock.get(
        url + f"&size={size}",
        json=_mock_one_page_reponse(0, size, total_pages, total_elements),
    )
    requests_mock.get(
        url + f"&size={size}&page=1",
        json=_mock_one_page_reponse(1, size, total_pages, total_elements),
    )
    requests_mock.get(
        url + f"&size={size}&page=2",
        json=_mock_one_page_reponse(2, size, total_pages, total_elements),
    )
    requests_mock.get(
        url + f"&size={size}&page=3",
        json=_mock_one_page_reponse(3, size, total_pages, total_elements),
    )
    res = storage_mock._query_paginated(url=url, limit=limit, size=size)
    assert len(res) == expected


def test_paginate_with_limit_smaller_page_size(storage_mock, requests_mock):
    """
    Test pagination with limit <= pagination size.
    """
    url = "http://some_url/assets"

    limit = 5
    size = limit
    total_pages = 2
    total_elements = 12
    expected = 5
    requests_mock.get(
        url + f"&size={limit}",
        json=_mock_one_page_reponse(0, size, total_pages, total_elements),
    )
    requests_mock.get(
        url + f"&size={limit}&page=1",
        json=_mock_one_page_reponse(0, size, total_pages, total_elements),
    )
    res = storage_mock._query_paginated(url=url, limit=limit, size=size)
    assert len(res) == expected


def test_get_assets(storage_mock):
    assets = storage_mock.get_assets()
    assert len(assets) == 1
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == ASSET_ID


@pytest.mark.live
def test_get_assets_live(storage_live):
    """
    SDK test account holds too few results to query multiple pages via pagination,
    needs to be mocked.
    """
    assets = storage_live.get_assets()
    assert len(assets) >= 2
    dates = [asset.info["createdAt"] for asset in assets]
    # default descending, newest to oldest.
    descending_dates = sorted(dates)[::-1]
    assert descending_dates == dates


def test_get_assets_pagination(auth_mock, requests_mock):
    """
    Mock result holds 2 pages, each with 50 results.
    """
    json_assets_paginated = {
        "data": {
            "content": [JSON_ASSET["data"]] * 50,
            "pageable": {
                "sort": {"sorted": True, "unsorted": False, "empty": False},
                "pageNumber": 0,
                "pageSize": 50,
                "offset": 0,
                "paged": True,
                "unpaged": False,
            },
            "totalPages": 2,
            "totalElements": 100,
            "last": True,
            "sort": {"sorted": True, "unsorted": False, "empty": False},
            "numberOfElements": 100,
            "first": True,
            "size": 50,
            "number": 0,
            "empty": False,
        },
        "error": None,
    }

    # assets pages
    url_storage_assets_paginated = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/"
        f"assets?format=paginated&sort=createdAt,asc&size=50"
    )
    requests_mock.get(url=url_storage_assets_paginated, json=json_assets_paginated)

    storage = Storage(auth=auth_mock)
    assets = storage.get_assets(limit=74, sortby="createdAt", descending=False)
    assert len(assets) == 74
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == ASSET_ID


def test_get_assets_raises_with_illegal_sorting_criteria(storage_mock):
    with pytest.raises(ValueError):
        storage_mock.get_assets(sortby="notavailable")


def test_get_orders(storage_mock):
    orders = storage_mock.get_orders()
    assert len(orders) == 1
    assert isinstance(orders[0], Order)
    assert orders[0].order_id == ORDER_ID


@pytest.mark.live
def test_get_orders_live(storage_live):
    """
    SDK test account holds too few results to query multiple pages via pagination,
    needs to be mocked.
    """
    orders = storage_live.get_orders()
    assert len(orders) >= 1
    dates = [order.info["createdAt"] for order in orders]
    # default descending, newest to oldest.
    descending_dates = sorted(dates)[::-1]
    assert descending_dates == dates


def test_get_orders_raises_with_illegal_sorting_criteria(storage_mock):
    with pytest.raises(ValueError):
        storage_mock.get_orders(sortby="notavailable")


def test_get_orders_pagination(auth_mock, requests_mock):
    """
    Mock result holds 2 pages, each with 50 results.
    """
    json_orders_paginated = {
        "data": {
            "content": [JSON_ORDER["data"]] * 50,
            "pageable": {
                "sort": {"sorted": True, "unsorted": False, "empty": False},
                "pageNumber": 0,
                "pageSize": 50,
                "offset": 0,
                "paged": True,
                "unpaged": False,
            },
            "totalPages": 2,
            "totalElements": 100,
            "last": True,
            "sort": {"sorted": True, "unsorted": False, "empty": False},
            "numberOfElements": 100,
            "first": True,
            "size": 50,
            "number": 0,
            "empty": False,
        },
        "error": None,
    }

    # assets pages
    url_storage_orders_paginated = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/"
        f"orders?format=paginated&sort=createdAt,asc&size=50"
    )
    requests_mock.get(url=url_storage_orders_paginated, json=json_orders_paginated)

    storage = Storage(auth=auth_mock)
    orders = storage.get_orders(limit=74, sortby="createdAt", descending=False)
    assert len(orders) == 74
    assert isinstance(orders[0], Order)
    assert orders[0].order_id == ORDER_ID
