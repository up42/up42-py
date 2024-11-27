import pystac_client
import pytest

from up42 import asset, order, storage

from .fixtures import fixtures_globals as constants


def test_init(storage_mock):
    assert isinstance(storage_mock, storage.Storage)
    assert storage_mock.workspace_id == constants.WORKSPACE_ID


def test_pystac_client_property(storage_mock):
    up42_pystac_client = storage_mock.pystac_client
    isinstance(up42_pystac_client, pystac_client.Client)


def test_get_assets(storage_mock):
    assets = storage_mock.get_assets()
    assert len(assets) == 1
    assert isinstance(assets[0], asset.Asset)
    assert assets[0].asset_id == constants.ASSET_ID


def test_get_assets_pagination(auth_mock, requests_mock):
    """
    SDK test account holds too few assets to query multiple pages via pagination,
    needs to be mocked.

    Mock result holds 2 pages, each with 50 results.
    """
    json_assets_paginated = {
        "content": [constants.JSON_ASSET] * 50,
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
    url_storage_assets_paginated = f"{constants.API_HOST}/v2/assets?sort=createdAt,asc&size=50"
    requests_mock.get(url=url_storage_assets_paginated, json=json_assets_paginated)

    storage_results = storage.Storage(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
    assets = storage_results.get_assets(limit=74, sortby="createdAt", descending=False)
    assert len(assets) == 74
    assert isinstance(assets[0], asset.Asset)
    assert assets[0].asset_id == constants.ASSET_ID


def test_get_orders(storage_mock):
    orders = storage_mock.get_orders(order_type="ARCHIVE", tags=["project-7", "optical"])
    assert len(orders) == 1
    assert isinstance(orders[0], order.Order)
    assert orders[0].order_id == constants.ORDER_ID


@pytest.mark.parametrize(
    "params, expected_payload, expected_results",
    [
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": None,
            },
            constants.JSON_ORDERS,
            constants.JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": ["CREATED", "FULFILLED"],
                "name": None,
            },
            constants.JSON_ORDERS,
            constants.JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": ["TEST"],
                "name": None,
            },
            constants.JSON_ORDERS,
            constants.JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": True,
                "return_json": False,
                "order_type": "TASKING",
                "statuses": ["CREATED"],
                "name": None,
            },
            constants.JSON_ORDERS,
            [
                {
                    "id": constants.ORDER_ID,
                    "userId": constants.USER_ID,
                    "workspaceId": constants.WORKSPACE_ID,
                    "dataProvider": "OneAtlas",
                    "status": "FULFILLED",
                    "createdAt": "2021-01-18T16:18:16.105851Z",
                    "updatedAt": "2021-01-18T16:21:31.966805Z",
                    "assets": ["363f89c1-3586-4b14-9a49-03a890c3b593"],
                    "createdBy": {
                        "id": constants.USER_ID,
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
            constants.JSON_ORDERS,
            constants.JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": False,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": None,
            },
            constants.JSON_ORDERS,
            constants.JSON_ORDERS["content"],
        ),
        (
            {
                "workspace_orders": False,
                "return_json": True,
                "order_type": "TASKING",
                "statuses": None,
                "name": None,
            },
            constants.JSON_ORDERS,
            constants.JSON_ORDERS["content"],
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
def test_get_orders_v2_endpoint_params(auth_mock, requests_mock, params, expected_payload, expected_results):
    allowed_statuses = {entry.value for entry in storage.AllowedStatuses}
    endpoint_statuses = set(params["statuses"]) & allowed_statuses if params["statuses"] else []
    url_params = "&".join(
        [
            "sort=createdAt%2Cdesc",
            (f"workspaceId={constants.WORKSPACE_ID}" if params["workspace_orders"] else ""),
            f"""displayName={params["name"]}""" if params["name"] else "",
            *[f"status={status}" for status in endpoint_statuses],
            "size=50",
        ]
    )

    url_storage_assets_paginated = f"{constants.API_HOST}/v2/orders?{url_params}"

    requests_mock.get(url=url_storage_assets_paginated, json=expected_payload)
    if not params["return_json"]:
        expected_results = [
            order.Order(
                order_id=output["id"],
                order_info=output,
            )
            for output in expected_results
        ]
    storage_results = storage.Storage(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
    orders = storage_results.get_orders(**params)
    assert orders == expected_results


def test_get_orders_raises_with_illegal_sorting_criteria(storage_mock):
    with pytest.raises(ValueError):
        storage_mock.get_orders(sortby="notavailable")


def test_get_orders_pagination(auth_mock, requests_mock):
    """
    Mock result holds 2 pages, each with 50 results.
    """
    json_orders_paginated = {
        "content": [constants.JSON_ORDER["data"]] * 50,
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
        f"{constants.API_HOST}/v2/orders?sort=createdAt,asc&workspaceId={constants.WORKSPACE_ID}&size=50"
    )
    requests_mock.get(url=url_storage_orders_paginated, json=json_orders_paginated)

    storage_results = storage.Storage(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
    orders = storage_results.get_orders(limit=74, sortby="createdAt", descending=False)
    assert len(orders) == 74
    assert isinstance(orders[0], order.Order)
    assert orders[0].order_id == constants.ORDER_ID
