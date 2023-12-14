import json
import os
from pathlib import Path

import pytest

from ..context import Order
from .fixtures_globals import (
    ASSET_ORDER_ID,
    JSON_ORDER_STAC,
    JSON_STAC_CATALOG_RESPONSE,
    ORDER_ID,
    URL_STAC_CATALOG,
    WORKSPACE_ID,
)

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


JSON_STAC_ORDER_EMPTY = {
    "links": [
        {
            "href": "https://api.up42.com/v2/assets/stac/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/",
            "rel": "parent",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/search",
            "rel": "self",
            "type": "application/json",
        },
    ],
    "type": "FeatureCollection",
    "features": [],
}


@pytest.fixture()
def order_mock(auth_mock, requests_mock):
    url_order_info = f"{auth_mock._endpoint()}/v2/orders/{ORDER_ID}"

    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/order_data/archive_order_info.json",
        encoding="utf-8",
    ) as json_file:
        json_oder_schenma = json.load(json_file)
        requests_mock.get(url=url_order_info, json=json_oder_schenma)

    requests_mock.get(url=URL_STAC_CATALOG, json=JSON_STAC_CATALOG_RESPONSE)

    url_asset_stac_info = f"{auth_mock._endpoint()}/v2/assets/stac/search"
    requests_mock.post(
        url_asset_stac_info,
        [{"json": JSON_ORDER_STAC}, {"json": JSON_STAC_ORDER_EMPTY}],
    )
    url_asset_info = f"{auth_mock._endpoint()}/v2/assets/{ASSET_ORDER_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=JSON_ORDER_ASSET)

    return Order(auth=auth_mock, order_id=ORDER_ID)


@pytest.fixture()
def order_live(auth_live):
    return Order(auth=auth_live, order_id=os.getenv("TEST_UP42_ORDER_ID"))
