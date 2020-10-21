import json
from pathlib import Path

import pytest
import geopandas as gpd
import pandas as pd
import requests

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    tools_mock,
    auth_live,
    tools_live,
)
from .context import Tools


@pytest.mark.parametrize("vector_format", ["geojson", "kml", "wkt"])
def test_read_vector_file_different_formats(tools_mock, vector_format):
    fp = Path(__file__).resolve().parent / f"mock_data/aoi_berlin.{vector_format}"
    fc = tools_mock.read_vector_file(filename=fp)
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"


def test_read_vector_file_as_df(tools_mock):
    fp = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    df = tools_mock.read_vector_file(filename=fp, as_dataframe=True)
    assert isinstance(df, gpd.GeoDataFrame)
    assert df.crs.to_epsg() == 4326


def test_get_example_aoi(tools_mock):
    fc = tools_mock.get_example_aoi("Berlin")
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"


def test_get_blocks(tools_mock, requests_mock):
    url_get_blocks = f"{tools_mock.auth._endpoint()}/blocks"
    requests_mock.get(
        url=url_get_blocks,
        json={
            "data": [
                {"id": "789-2736-212", "name": "tiling"},
                {"id": "789-2736-212", "name": "sharpening"},
            ],
            "error": {},
        },
    )
    blocks = tools_mock.get_blocks()
    assert isinstance(blocks, dict)
    assert "tiling" in list(blocks.keys())


@pytest.mark.live
def test_get_blocks_live(tools_live):
    blocks = tools_live.get_blocks(basic=False)
    assert isinstance(blocks, list)
    blocknames = [block["name"] for block in blocks]
    assert "tiling" in blocknames


def test_get_blocks_not_basic_dataframe(tools_mock, requests_mock):
    url_get_blocks = f"{tools_mock.auth._endpoint()}/blocks"
    json_get_blocks = {
        "data": [
            {"id": "789-2736-212", "name": "tiling"},
            {"id": "789-2736-212", "name": "sharpening"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_get_blocks, json=json_get_blocks)

    blocks_df = tools_mock.get_blocks(basic=False, as_dataframe=True)
    assert isinstance(blocks_df, pd.DataFrame)
    assert "tiling" in blocks_df["name"].to_list()


def test_get_block_details(tools_mock, requests_mock):
    block_id = "273612-13"
    url_get_blocks_details = f"{tools_mock.auth._endpoint()}/blocks/{block_id}"
    requests_mock.get(
        url=url_get_blocks_details,
        json={
            "data": {"id": "273612-13", "name": "tiling", "createdAt": "123"},
            "error": {},
        },
    )
    details = tools_mock.get_block_details(block_id=block_id)
    assert isinstance(details, dict)
    assert details["id"] == block_id
    assert "createdAt" in details


@pytest.mark.live
def test_get_block_details_live(tools_live):
    tiling_id = "3e146dd6-2b67-4d6e-a422-bb3d973e32ff"

    details = tools_live.get_block_details(block_id=tiling_id)
    assert isinstance(details, dict)
    assert details["id"] == tiling_id
    assert "createdAt" in details


def test_validate_manifest(tools_mock, requests_mock):
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    url_validate_mainfest = f"{tools_mock.auth._endpoint()}/validate-schema/block"
    requests_mock.post(
        url=url_validate_mainfest,
        json={"data": {"valid": True, "errors": []}, "error": {}},
    )

    result = tools_mock.validate_manifest(path_or_json=fp)
    assert result == {"valid": True, "errors": []}


@pytest.mark.live
def test_validate_manifest_valid_live(tools_live):
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    result = tools_live.validate_manifest(path_or_json=fp)
    assert result == {"valid": True, "errors": []}


@pytest.mark.live
def test_validate_manifest_invalid_live(tools_live):
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    with open(fp) as src:
        mainfest_json = json.load(src)
        mainfest_json.update(
            {
                "_up42_specification_version": 1,
                "input_capabilities": {
                    "invalidtype": {"up42_standard": {"format": "GTiff"}}
                },
            }
        )
    with pytest.raises(requests.exceptions.RequestException):
        tools_live.validate_manifest(path_or_json=mainfest_json)
