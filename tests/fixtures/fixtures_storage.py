import pytest

from up42.storage import Storage

from .fixtures_globals import (
    API_HOST,
    ASSET_ID,
    JSON_ASSET,
    JSON_ASSETS,
    JSON_ORDER,
    JSON_ORDERS,
    JSON_STORAGE_STAC,
    ORDER_ID,
    PYSTAC_MOCK_CLIENT,
)


@pytest.fixture()
def storage_mock(auth_mock, requests_mock):
    # pystac client authentication
    url_pystac_client = f"{API_HOST}/v2/assets/stac"
    requests_mock.get(url=url_pystac_client, json=PYSTAC_MOCK_CLIENT)

    # assets
    url_storage_assets = f"{API_HOST}/v2/assets"
    requests_mock.get(url=url_storage_assets, json=JSON_ASSETS)

    # storage stac
    url_storage_stac = f"{API_HOST}/v2/assets/stac/search"
    requests_mock.post(url=url_storage_stac, json=JSON_STORAGE_STAC)

    # asset info
    url_asset_info = f"{API_HOST}/v2/assets/{ASSET_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)

    # orders
    url_storage_orders = (
        f"{API_HOST}/v2/orders"
        "?sort=createdAt,desc&workspaceId=workspace_id_123"
        "&type=ARCHIVE&tags=project-7&tags=optical&size=50"
    )
    requests_mock.get(url=url_storage_orders, json=JSON_ORDERS)

    url_storage_orders_params = (
        f"{API_HOST}/v2/orders"
        "?sort=createdAt,desc"
        "&displayName=Test&type=ARCHIVE&status=FULFILLED&status=PLACED&size=50"
    )
    requests_mock.get(url=url_storage_orders_params, json=JSON_ORDERS)

    # orders info
    url_order_info = f"{API_HOST}/v2/orders/{ORDER_ID}"
    requests_mock.get(url=url_order_info, json=JSON_ORDER)

    storage = Storage(auth=auth_mock)

    return storage


@pytest.fixture()
def storage_live(auth_live):
    storage = Storage(auth=auth_live)
    return storage
