import os

import pytest

from .fixtures_globals import ASSET_ID, JSON_ASSET, DOWNLOAD_URL, JSON_STORAGE_STAC

from ..context import (
    Asset,
)


@pytest.fixture()
def asset_mock(auth_mock, requests_mock):
    # asset info
    url_asset_info = f"{auth_mock._endpoint()}/v2/assets/{ASSET_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)

    # asset stac info
    url_asset_stac_info = f"{auth_mock._endpoint()}/v2/assets/stac/search"
    requests_mock.post(url=url_asset_stac_info, json=JSON_STORAGE_STAC)

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

    asset = Asset(auth=auth_mock, asset_id=ASSET_ID)

    return asset


@pytest.fixture()
def asset_live(auth_live):
    asset = Asset(auth=auth_live, asset_id=os.getenv("TEST_UP42_ASSET_ID"))
    return asset
