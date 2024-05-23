import pytest

from up42 import storage

from . import fixtures_globals as constants


@pytest.fixture()
def storage_mock(auth_mock, requests_mock):
    # pystac client authentication
    requests_mock.get(url=constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)

    # assets
    url_storage_assets = f"{constants.API_HOST}/v2/assets"
    requests_mock.get(url=url_storage_assets, json=constants.JSON_ASSETS)

    # storage stac
    requests_mock.post(url=constants.URL_STAC_SEARCH, json=constants.STAC_SEARCH_RESPONSE)

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
