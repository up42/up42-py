import pytest

from up42 import storage

from . import fixtures_globals as constants


@pytest.fixture()
def storage_mock(auth_mock, requests_mock):
    # pystac client authentication
    url_pystac_client = f"{constants.API_HOST}/v2/assets/stac"
    requests_mock.get(url=url_pystac_client, json=constants.PYSTAC_MOCK_CLIENT)

    # assets
    url_storage_assets = f"{constants.API_HOST}/v2/assets"
    requests_mock.get(url=url_storage_assets, json=constants.JSON_ASSETS)

    # storage stac
    url_storage_stac = f"{constants.API_HOST}/v2/assets/stac/search"
    requests_mock.post(url=url_storage_stac, json=constants.JSON_STORAGE_STAC)

    # asset info
    url_asset_info = f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=constants.JSON_ASSET)

    # orders
    url_storage_orders = (
        f"{constants.API_HOST}/v2/orders"
        "?sort=createdAt,desc&workspaceId=workspace_id_123"
        "&type=ARCHIVE&tags=project-7&tags=optical&size=50"
    )
    requests_mock.get(url=url_storage_orders, json=constants.JSON_ORDERS)

    url_storage_orders_params = (
        f"{constants.API_HOST}/v2/orders"
        "?sort=createdAt,desc"
        "&displayName=Test&type=ARCHIVE&status=FULFILLED&status=PLACED&size=50"
    )
    requests_mock.get(url=url_storage_orders_params, json=constants.JSON_ORDERS)

    # orders info
    url_order_info = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
    requests_mock.get(url=url_order_info, json=constants.JSON_ORDER)
    return storage.Storage(auth=auth_mock)


@pytest.fixture()
def storage_live(auth_live):
    return storage.Storage(auth=auth_live)
