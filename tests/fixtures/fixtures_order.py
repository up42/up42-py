import json
import os
from pathlib import Path

import pytest

from ..context import Order
from .fixtures_globals import ASSET_ORDER_ID, ORDER_ID, WORKSPACE_ID

JSON_ORDER_ASSET = {
    "accountId": "69353acb-f942-423f-8f32-11d6d67caa77",
    "createdAt": "2022-12-07T14:25:34.968Z",
    "updatedAt": "2022-12-07T14:25:34.968Z",
    "id": ASSET_ORDER_ID,
    "name": "string",
    "size": 256248634,
    "workspaceId": WORKSPACE_ID,
    "order": {"id": "string", "status": "string", "hostId": "string"},
    "source": "ARCHIVE",
    "productId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "contentType": "string",
    "producerName": "string",
    "collectionName": "string",
    "geospatialMetadataExtraction": "SUCCESSFUL",
    "title": "string",
    "tags": ["string"],
}

JSON_GET_ASSETS_RESPONSE = {
    "content": [JSON_ORDER_ASSET],
    "pageable": {
        "sort": {"sorted": True, "unsorted": False, "empty": False},
        "pageNumber": 0,
        "pageSize": 10,
        "offset": 0,
        "paged": True,
        "unpaged": False,
    },
    "totalPages": 1,
    "totalElements": 1,
    "last": True,
    "sort": {"sorted": True, "unsorted": False, "empty": False},
    "numberOfElements": 1,
    "first": True,
    "size": 10,
    "number": 0,
    "empty": False,
}


def read_test_order_info() -> dict:
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/order_data/archive_order_info.json",
        encoding="utf-8",
    ) as json_file:
        return json.load(json_file)


@pytest.fixture
def order_mock(auth_mock, requests_mock):
    url_order_info = f"{auth_mock._endpoint()}/v2/orders/{ORDER_ID}"
    requests_mock.get(url=url_order_info, json=read_test_order_info())

    return Order(auth=auth_mock, order_id=ORDER_ID)


@pytest.fixture()
def order_live(auth_live):
    return Order(auth=auth_live, order_id=os.getenv("TEST_UP42_ORDER_ID"))
