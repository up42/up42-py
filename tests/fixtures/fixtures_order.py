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

JSON_GET_ORDERS_RESPONSE = {
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

JSON_ORDER_STAC_NO_ASSET_ID = {
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
    "features": [
        {
            "assets": {
                "data": {
                    "href": f"https://api.up42.com/v2/assets/{ASSET_ORDER_ID}",
                    "title": "Data",
                    "description": "Storage Data",
                    "type": "application/zip",
                    "roles": ["data"],
                }
            },
            "links": [
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/7947d269-117a-4954-8cab-adf6be623ca9/items/363e7831-48ff-4311-83c1-a37d3ef54b66",
                    "rel": "self",
                    "type": "application/geo+json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/7947d269-117a-4954-8cab-adf6be623ca9",
                    "rel": "parent",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/7947d269-117a-4954-8cab-adf6be623ca9",
                    "rel": "collection",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/",
                    "rel": "root",
                    "type": "application/json",
                },
            ],
            "stac_extensions": [
                "https://stac-extensions.github.io/view/v1.0.0/schema.json",
                "https://api.up42.com/stac-extensions/up42-system/v1.0.0/schema.json",
                "https://api.up42.com/stac-extensions/up42-order/v1.0.0/schema.json",
                "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
                "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                "https://api.up42.com/stac-extensions/up42-product/v1.0.0/schema.json",
            ],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [13.355241206273849, 52.52676203252064],
                        [13.355300478383226, 52.52675386522252],
                        [13.356956160907195, 52.5250505720669],
                        [13.35726007462071, 52.52441192697056],
                        [13.357032090123967, 52.52360855273764],
                        [13.350989718479445, 52.524360678086275],
                        [13.351542524330116, 52.5263284439625],
                        [13.355241206273849, 52.52676203252064],
                    ]
                ],
            },
            "bbox": [
                13.350989718479445,
                52.52360855273764,
                13.35726007462071,
                52.52676203252064,
            ],
            "properties": {
                "gsd": 0.819460017886369,
                "title": "DS_PHR1A_202009301038498_FR1_PX_E013N52_0513_00365_R1C1",
                "datetime": "2020-09-30T10:39:26.600000+00:00",
                "platform": "PHR-1A",
                "proj:epsg": 32633,
                "end_datetime": "2020-09-30T10:39:26.600000+00:00",
                "view:azimuth": 179.66501598193926,
                "constellation": "PHR",
                "up42-order:id": "da2310a2-c7fb-42ed-bead-fb49ad862c67",
                "eo:cloud_cover": 0.0,
                "start_datetime": "2020-09-30T10:39:26.600000+00:00",
                "view:sun_azimuth": 174.870231299609,
                "up42-system:source": "ARCHIVE",
                "view:sun_elevation": 34.28921400755616,
                "view:incidence_angle": 25.943721144567032,
                "up42-product:modality": "multispectral",
                "up42-product:data_type": "raster",
                "up42-system:account_id": "some-account-id",
                "up42-product:product_id": "4f1b2f62-98df-4c74-81f4-5dce45deee99",
                "up42-system:workspace_id": "some-workspace-id",
                "up42-product:collection_name": "phr",
                "up42-system:metadata_version": "0.0.4",
                "created": "2023-02-17T11:33:18.876308+00:00",
                "updated": "2023-03-13T15:33:06.800619+00:00",
            },
            "type": "Feature",
            "stac_version": "1.0.0",
            "id": "363e7831-48ff-4311-83c1-a37d3ef54b66",
            "collection": "7947d269-117a-4954-8cab-adf6be623ca9",
        }
    ],
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
    url_asset_info = f"{auth_mock._endpoint()}/v2/assets?sort=createdAt%2Cdesc&search={ORDER_ID}&size=50"
    requests_mock.get(url=url_asset_info, json=JSON_GET_ORDERS_RESPONSE)

    return Order(auth=auth_mock, order_id=ORDER_ID)


@pytest.fixture()
def order_live(auth_live):
    return Order(auth=auth_live, order_id=os.getenv("TEST_UP42_ORDER_ID"))
