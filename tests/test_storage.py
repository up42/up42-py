import datetime
import copy

import pytest
import requests

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
    JSON_STORAGE_STAC,
)

def match_request_text(request):
    return 'token' in request.body

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


def test__search_stac(storage_mock):
    geometry = {
        "coordinates": [
            [
                [13.353338545805542, 52.52576354784705],
                [13.353338545805542, 52.52400476917347],
                [13.355812219301214, 52.52400476917347],
                [13.355812219301214, 52.52576354784705],
                [13.353338545805542, 52.52576354784705],
            ]
        ],
        "type": "Polygon",
    }
    stac_results = storage_mock._search_stac(
        acquired_after="2021-05-30",
        acquired_before=datetime.datetime(2023, 5, 17),
        geometry=geometry,
        custom_filter={"op": "gte", "args": [{"property": "eo:cloud_cover"}, 10]},
    )
    assert isinstance(stac_results, list)
    assert stac_results[0]["assets"]


@pytest.mark.live
def test__search_stac_live(storage_live):
    geometry = {
        "coordinates": [
            [
                [13.353338545805542, 52.52576354784705],
                [13.353338545805542, 52.52400476917347],
                [13.355812219301214, 52.52400476917347],
                [13.355812219301214, 52.52576354784705],
                [13.353338545805542, 52.52576354784705],
            ]
        ],
        "type": "Polygon",
    }
    stac_results = storage_live._search_stac(
        acquired_after="2021-05-30",
        acquired_before=datetime.datetime(2023, 5, 17),
        geometry=geometry,
        custom_filter={"op": "gte", "args": [{"property": "eo:cloud_cover"}, 10]},
    )
    assert isinstance(stac_results, dict)
    assert stac_results["features"][0]["assets"]
    # TODO: assertions


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
    res = storage_mock._query_paginated_endpoints(url=url, limit=limit, size=size)
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
    res = storage_mock._query_paginated_endpoints(url=url, limit=limit, size=size)
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
    dates = [asset.info["createdAt"] for asset in assets]
    # default descending, newest to oldest.
    descending_dates = sorted(dates)[::-1]
    assert descending_dates == dates


def test_get_assets_with_search_stac(storage_mock):
    assets = storage_mock.get_assets(acquired_after="2021-05-30")
    assert len(assets) == 1
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == ASSET_ID


@pytest.mark.live
def test_get_assets_with_stac_query_live(storage_live):
    filter_geometry = {
        "coordinates": [
            [
                [13.353338545805542, 52.52576354784705],
                [13.353338545805542, 52.52400476917347],
                [13.355812219301214, 52.52400476917347],
                [13.355812219301214, 52.52576354784705],
                [13.353338545805542, 52.52576354784705],
            ]
        ],
        "type": "Polygon",
    }

    storage_live.get_assets(geometry=filter_geometry)
    # TODO assertions


def test_get_assets_with_stac_query_pagination(storage_mock, requests_mock):
    """
    Test the stac query pagination by checking the token element in the payload.
    if the response has the token element in the body, then the _query_paginated_stac_search 
    retrieves the next page and append the features in the return list. 
    Otherwise, return the current list of features. 
    """
    url_storage_stac = f"http://some_url/assets/stac/search"
    stac_search_parameters = {
            "max_items": 100,
            "limit": 10000,
    }
    
    requests_mock.post(
        url_storage_stac,
        json=JSON_STORAGE_STAC,
    )

    json_storage_stac = copy.deepcopy(JSON_STORAGE_STAC)
    json_storage_stac["links"].pop(-1)

    requests_mock.post(
        url_storage_stac,
        additional_matcher=match_request_text,
        json=json_storage_stac,
    )

    resp = storage_mock._query_paginated_stac_search(url=url_storage_stac, stac_search_parameters=stac_search_parameters)
    assert len(resp) == 2

def test_get_assets_pagination(auth_mock, requests_mock):
    """
    SDK test account holds too few assets to query multiple pages via pagination,
    needs to be mocked.

    Mock result holds 2 pages, each with 50 results.
    """
    json_assets_paginated = {
        "content": [JSON_ASSET] * 50,
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
    }

    # assets pages
    url_storage_assets_paginated = (
        f"{auth_mock._endpoint()}/v2/assets?sort=createdAt,asc&size=50"
    )
    requests_mock.get(url=url_storage_assets_paginated, json=json_assets_paginated)

    storage = Storage(auth=auth_mock)
    assets = storage.get_assets(limit=74, sortby="createdAt", descending=False)
    assert len(assets) == 74
    assert isinstance(assets[0], Asset)
    assert assets[0].asset_id == ASSET_ID


@pytest.mark.live
def test_get_assets_raise_error_live(storage_live):
    """
    Api v2 error format is handled in the auth request method
    This tests asserts if the api v2 error response is correct.
    """
    with pytest.raises(requests.exceptions.RequestException) as e:
        storage_live.get_assets(workspace_id="a")
    assert "title" in str(e.value)


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
