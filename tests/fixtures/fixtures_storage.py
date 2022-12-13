import pytest

from .fixtures_globals import (
    JSON_ASSETS,
    JSON_ASSET,
    ASSET_ID,
    JSON_ORDERS,
    JSON_ORDER,
    ORDER_ID,
)

from ..context import (
    Storage,
)


@pytest.fixture()
def storage_mock(auth_mock, requests_mock):
    # assets
    url_storage_assets = f"{auth_mock._endpoint()}/v2/assets"
    requests_mock.get(url=url_storage_assets, json=JSON_ASSETS)

    # asset info
    url_asset_info = f"{auth_mock._endpoint()}/v2/assets/{ASSET_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)

    # orders
    url_storage_assets = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders"
    )
    requests_mock.get(url=url_storage_assets, json=JSON_ORDERS)

    # orders info
    url_order_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/{ORDER_ID}"
    )
    requests_mock.get(url=url_order_info, json=JSON_ORDER)

    storage = Storage(auth=auth_mock)

    return storage


@pytest.fixture()
def storage_live(auth_live):
    storage = Storage(auth=auth_live)
    return storage
