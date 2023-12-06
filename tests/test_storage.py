import copy
import datetime

import pystac
import pystac_client
import pytest
import requests

# pylint: disable=unused-import
from .context import AllowedStatuses, Asset, Order, Storage
from .fixtures import (
    ASSET_ID,
    JSON_ASSET,
    JSON_ORDER,
    JSON_ORDERS,
    JSON_STORAGE_STAC,
    ORDER_ID,
    WORKSPACE_ID,
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    storage_live,
    storage_mock,
    username_test_live,
)


def test_init(storage_mock):
    assert isinstance(storage_mock, Storage)
    assert storage_mock.workspace_id == WORKSPACE_ID


def test_pystac_client_property(storage_mock):
    up42_pystac_client = storage_mock.pystac_client
    isinstance(up42_pystac_client, pystac_client.Client)


@pytest.mark.live
def test_pystac_client_property_live(storage_live):
    up42_pystac_client = storage_live.pystac_client
    isinstance(up42_pystac_client, pystac_client.Client)
    stac_collections = up42_pystac_client.get_collections()
    assert isinstance(stac_collections.__next__(), pystac.Collection)


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
    res = storage_mock._query_paginated_endpoints(url=url, limit=limit, size=size)
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
    with pytest.raises(ValueError) as e:
        storage_live.get_assets(
            created_after="2020-01-01",
            created_before="2023-01-01",
            acquired_after="2020-01-01",
            acquired_before="2023-01-01",
        )
    assert "no longer supported" in str(e.value)


@pytest.mark.live
def test_get_assets_by_source_live(storage_live):
    assets = storage_live.get_assets(sources=["ARCHIVE"])
    assert len(assets) >= 2


def test_get_assets_with_search_stac(storage_mock):
    with pytest.raises(ValueError) as e:
        storage_mock.get_assets(
            created_after="2020-01-01",
            created_before="2023-01-01",
            acquired_after="2020-01-01",
            acquired_before="2023-01-01",
            tags=["project-7", "optical"],
        )
        assert "no longer supported" in str(e.value)


def test_get_assets_with_stac_query_pagination(storage_mock, requests_mock):
    """
    Test the stac query pagination by checking the token element in the payload.
    if the response has the token element in the body, then the _query_paginated_stac_search
    retrieves the next page and append the features in the return list.
    Otherwise, return the current list of features.
    """

    def match_request_text(request):
        return "token" in request.body

    url_storage_stac = "http://some_url/assets/stac/search"
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

    resp = storage_mock._query_paginated_stac_search(
        url=url_storage_stac, stac_search_parameters=stac_search_parameters
    )
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
    orders = storage_mock.get_orders(
        order_type="ARCHIVE", tags=["project-7", "optical"]
    )
    assert len(orders) == 1
    assert isinstance(orders[0], Order)
    assert orders[0].order_id == ORDER_ID


@pytest.mark.parametrize(
    "params, expected_output_endpoint, expected_output_method",
    [
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": None,
            },
            JSON_ORDERS,
            JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": ["CREATED", "FULFILLED"],
                "name": None,
            },
            JSON_ORDERS,
            JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": ["TEST"],
                "name": None,
            },
            JSON_ORDERS,
            JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": False,
                "order_type": "TASKING",
                "statuses": ["CREATED"],
                "name": None,
            },
            JSON_ORDERS,
            [
                {
                    "id": "ddb207c0-3b7f-4186-bc0b-c033f0d2f32b",
                    "userId": "1094497b-11d8-4fb8-9d6a-5e24a88aa825",
                    "workspaceId": "workspace_id_123",
                    "dataProvider": "OneAtlas",
                    "status": "FULFILLED",
                    "createdAt": "2021-01-18T16:18:16.105851Z",
                    "updatedAt": "2021-01-18T16:21:31.966805Z",
                    "assets": ["363f89c1-3586-4b14-9a49-03a890c3b593"],
                    "createdBy": {
                        "id": "1094497b-11d8-4fb8-9d6a-5e24a88aa825",
                        "type": "USER",
                    },
                    "updatedBy": {"id": "system", "type": "INTERNAL"},
                },
            ],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": "Testing",
            },
            JSON_ORDERS,
            JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": False,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": None,
            },
            JSON_ORDERS,
            JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": False,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": None,
            },
            JSON_ORDERS,
            JSON_ORDERS["content"],
        ),
    ],
    ids=[
        "Sc 1: statuses None, workspace_orders and return_json True, name None",
        "Sc 2: statuses allowed, workspace_orders and return_json True, name None",
        "Sc 3: statuses non allowed, workspace_orders and return_json True, name None",
        "Sc 4: statuses allowed, workspace_orders True, return_json False, name None -> orders output expected",
        "Sc 5: statuses None, workspace_orders and return_json True, name Test",
        "Sc 6: Workspace Orders, Return JSON True, Statuses Test, name None",
        "Sc 7: statuses None, workspace_orders False, Return JSON True, name None",
    ],
)
def test_get_orders_v2_endpoint_params(
    auth_mock, requests_mock, params, expected_output_endpoint, expected_output_method
):
    workspace_url_param = (
        f"&workspaceId={WORKSPACE_ID}" if params["workspace_orders"] else ""
    )

    allowed_statuses = {entry.value for entry in AllowedStatuses}
    endpoint_statuses = (
        set(params["statuses"]) & allowed_statuses if params["statuses"] else None
    )
    statuses_url_param = (
        f"""&status={"&status=".join([status for status in endpoint_statuses])}"""
        if endpoint_statuses
        else ""
    )

    name_url_param = f"""&displayName={params["name"]}""" if params["name"] else ""

    url_storage_assets_paginated = (
        f"{auth_mock._endpoint()}/v2/orders?sort=createdAt%2Cdesc{workspace_url_param}{name_url_param}"
        f"&type={params['order_type']}{statuses_url_param}&size=50"
    )
    requests_mock.get(url=url_storage_assets_paginated, json=expected_output_endpoint)
    if not params["return_json"]:
        expected_results = [
            Order(
                auth=auth_mock,
                order_id=output["id"],
                order_info=output,
            )
            for output in expected_output_method
        ]
    else:
        expected_results = expected_output_method

    storage = Storage(auth=auth_mock)
    orders = storage.get_orders(**params)

    for order, expected_result in zip(orders, expected_results):
        assert order == expected_result


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

    orders_tags = storage_live.get_orders(tags=["Test"])
    assert len(orders_tags) >= 0


def test_get_orders_raises_with_illegal_sorting_criteria(storage_mock):
    with pytest.raises(ValueError):
        storage_mock.get_orders(sortby="notavailable")


def test_get_orders_pagination(auth_mock, requests_mock):
    """
    Mock result holds 2 pages, each with 50 results.
    """
    json_orders_paginated = {
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
    }

    # assets pages
    url_storage_orders_paginated = (
        f"{auth_mock._endpoint()}/v2/"
        f"orders?sort=createdAt,asc&workspaceId={auth_mock.workspace_id}&size=50"
    )
    requests_mock.get(url=url_storage_orders_paginated, json=json_orders_paginated)

    storage = Storage(auth=auth_mock)
    orders = storage.get_orders(limit=74, sortby="createdAt", descending=False)
    assert len(orders) == 74
    assert isinstance(orders[0], Order)
    assert orders[0].order_id == ORDER_ID
