import uuid

import requests_mock as req_mock

import up42
from tests import constants
from up42 import catalog, order, storage, tasking


def test_should_initialize_objects(requests_mock: req_mock.Mocker):
    catalog_obj = up42.initialize_catalog()
    assert isinstance(catalog_obj, catalog.Catalog)

    storage_obj = up42.initialize_storage()
    assert isinstance(storage_obj, storage.Storage)
    assert storage_obj.workspace_id == constants.WORKSPACE_ID

    order_url = f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}"
    order_info = {
        "id": constants.ORDER_ID,
        "displayName": "display-name",
        "status": "some-status",
        "workspaceId": constants.WORKSPACE_ID,
        "accountId": "account-id",
        "type": "ARCHIVE",
    }
    requests_mock.get(url=order_url, json=order_info)
    order_obj = up42.initialize_order(order_id=constants.ORDER_ID)
    assert order_obj == order.Order.from_dict(order_info)

    asset_id = str(uuid.uuid4())

    asset_url = f"{constants.API_HOST}/v2/assets/{asset_id}/metadata"
    asset_info = {"id": asset_id, "other": "data"}
    requests_mock.get(url=asset_url, json=asset_info)
    asset_obj = up42.initialize_asset(asset_id=asset_id)
    assert asset_obj.info == asset_info

    result = up42.initialize_tasking()
    assert isinstance(result, tasking.Tasking)
