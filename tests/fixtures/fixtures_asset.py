import pathlib

import pytest

from up42 import asset

from . import fixtures_globals as constants


@pytest.fixture(name="asset_mock")
def _asset_mock(auth_mock, requests_mock):
    # asset info
    url_asset_info = f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID}/metadata"
    requests_mock.get(url=url_asset_info, json=constants.JSON_ASSET)

    # asset update
    updated_json_asset = constants.JSON_ASSET.copy()
    updated_json_asset["title"] = "some_other_title"
    updated_json_asset["tags"] = ["othertag1", "othertag2"]
    requests_mock.post(url=url_asset_info, json=updated_json_asset)

    # download url
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID}/download-url",
        json={"url": constants.DOWNLOAD_URL},
    )

    return asset.Asset(auth=auth_mock, asset_id=constants.ASSET_ID)


@pytest.fixture(name="asset_mock2")
def _asset_mock2(auth_mock, requests_mock):
    url_asset_info = f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID2}/metadata"
    requests_mock.get(url=url_asset_info, json={**constants.JSON_ASSET, "id": constants.ASSET_ID2})
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID2}/download-url",
        json={"url": constants.DOWNLOAD_URL2},
    )
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/assets/{constants.STAC_ASSET_ID}/download-url",
        json={"url": constants.STAC_ASSET_URL},
    )
    mock_file = pathlib.Path(__file__).resolve().parents[1] / "mock_data/aoi_berlin.geojson"
    with open(mock_file, "rb") as src_file:
        out_file = src_file.read()

    requests_mock.get(
        url=constants.STAC_ASSET_URL,
        content=out_file,
    )
    return asset.Asset(auth=auth_mock, asset_id=constants.ASSET_ID2)


@pytest.fixture(params=["asset_mock", "asset_mock2"])
def assets_fixture(request, asset_mock, asset_mock2):
    mocks = {
        "asset_mock": {
            "asset_fixture": asset_mock,
            "download_url": constants.DOWNLOAD_URL,
            "outfile_name": "output.tgz",
        },
        "asset_mock2": {
            "asset_fixture": asset_mock2,
            "download_url": constants.DOWNLOAD_URL2,
            "outfile_name": "DS_SPOT6_202206240959075_FR1_FR1_SV1_SV1_E013N52_01709.tgz",
        },
    }
    return mocks[request.param]
