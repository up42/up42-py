import datetime
import os
import pytest
from pystac import Item, ItemCollection
from pystac.collection import Extent, SpatialExtent, TemporalExtent
from pystac_client import CollectionClient

from ..context import Asset
from .fixtures_globals import (
    ASSET_ID,
    ASSET_ID2,
    DOWNLOAD_URL,
    DOWNLOAD_URL2,
    JSON_ASSET,
    JSON_STORAGE_STAC,
    STAC_COLLECTION_ID,
)


@pytest.fixture()
def asset_mock(auth_mock, requests_mock):
    # asset info
    url_asset_info = f"{auth_mock._endpoint()}/v2/assets/{ASSET_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)

    mock_item_collection = ItemCollection(
        items=[
            Item(
                id="test",
                geometry=None,
                properties={},
                bbox=None,
                datetime=datetime.datetime.now(),
            )
        ]
    )

    url_asset_stac_info = f"{auth_mock._endpoint()}/v2/assets/stac/search"

    requests_mock.post(
        url_asset_stac_info,
        [
            {"json": JSON_STORAGE_STAC},
            {"json": JSON_STORAGE_STAC},
            {"json": mock_item_collection.to_dict()},
        ],
    )

    # asset stac item
    url_asset_stac = f"{auth_mock._endpoint()}/v2/assets/stac"

    catalog = {
        "type": "Catalog",
        "id": "up42-storage",
        "stac_version": "1.0.0",
        "description": "UP42 Storage STAC API",
        "links": [
            {
                "rel": "root",
                "href": "https://api.up42.com/v2/assets/stac",
                "type": "application/json",
                "title": "UP42 Storage",
            },
            {
                "rel": "data",
                "href": "https://api.up42.com/v2/assets/stac/collections",
                "type": "application/json",
            },
            {
                "rel": "search",
                "href": "https://api.up42.com/v2/assets/stac/search",
                "type": "application/json",
                "method": "POST",
            },
            {
                "rel": "self",
                "href": "https://api.up42.com/v2/assets/stac",
                "type": "application/json",
            },
        ],
        "stac_extensions": [],
        "conformsTo": [
            "https://api.stacspec.org/v1.0.0-rc.1/collections",
            "https://api.stacspec.org/v1.0.0-rc.1/core",
            "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/features-filter",
            "http://www.opengis.net/spec/ogcapi-features-4/1.0/conf/simpletx",
            "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter",
            "http://www.opengis.net/spec/cql2/1.0/conf/cql2-text",
            "https://api.stacspec.org/v1.0.0-rc.1/item-search",
            "https://api.stacspec.org/v1.0.0-rc.1/ogcapi-features/extensions/transaction",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter",
            "http://www.opengis.net/spec/cql2/1.0/conf/basic-cql2",
            "https://api.stacspec.org/v1.0.0-rc.1/ogcapi-features",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
            "https://api.stacspec.org/v1.0.0-rc.1/item-search#sort",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
        ],
        "title": "UP42 Storage",
    }
    requests_mock.get(url=url_asset_stac, json=catalog)

    # asset update
    updated_json_asset = JSON_ASSET.copy()
    updated_json_asset["title"] = "some_other_title"
    updated_json_asset["tags"] = ["othertag1", "othertag2"]
    requests_mock.post(url=url_asset_info, json=updated_json_asset)

    # download url
    requests_mock.post(
        url=f"{auth_mock._endpoint()}/v2/assets/{ASSET_ID}/download-url",
        json={"url": DOWNLOAD_URL},
    )

    # stac_info url
    mock_client = CollectionClient(
        id="up42-storage",
        description="UP42 Storage STAC API",
        extra_fields={"up42-system:asset_id": ASSET_ID},
        extent=Extent(
            spatial=SpatialExtent(
                bboxes=[
                    [
                        13.3783333333333,
                        52.4976111111112,
                        13.3844444444445,
                        52.5017222222223,
                    ]
                ]
            ),
            temporal=TemporalExtent(
                intervals=[
                    [datetime.datetime(2021, 5, 31), datetime.datetime(2021, 5, 31)]
                ]
            ),
        ),
    )
    requests_mock.get(
        url=f"{auth_mock._endpoint()}/v2/assets/stac/collections/{STAC_COLLECTION_ID}",
        json=mock_client.to_dict(),
    )

    asset = Asset(auth=auth_mock, asset_id=ASSET_ID)

    return asset


@pytest.fixture()
def asset_mock2(auth_mock, requests_mock):
    url_asset_info = f"{auth_mock._endpoint()}/v2/assets/{ASSET_ID2}/metadata"
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)
    requests_mock.post(
        url=f"{auth_mock._endpoint()}/v2/assets/{ASSET_ID2}/download-url",
        json={"url": DOWNLOAD_URL2},
    )
    asset = Asset(auth=auth_mock, asset_id=ASSET_ID2)
    return asset


@pytest.fixture()
def asset_live(auth_live):
    asset = Asset(auth=auth_live, asset_id=os.getenv("TEST_UP42_ASSET_ID"))
    return asset
