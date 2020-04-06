import json
from pathlib import Path

import pytest
import geopandas as gpd
from mock import patch
import requests_mock
import pandas as pd

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


def test_draw_aoi_raises_without_jupyter(tools_mock):
    with pytest.raises(ValueError):
        tools_mock.draw_aoi()


@patch("matplotlib.pyplot.show")
def test_plot_coverage(tools_mock):
    df = gpd.read_file(
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson",
        as_dataframe=True,
    )
    tools_mock.plot_coverage(df)


@patch("matplotlib.pyplot.show")
def test_plot_coverage_wrong_legend_column_ignores(tools_mock):
    df = gpd.read_file(
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson",
        as_dataframe=True,
    )
    tools_mock.plot_coverage(df, legend_column="abcdefgh")


@patch("matplotlib.pyplot.show")
def test_plot_quicklook(tools_mock):
    fp_quicklook = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    tools_mock.quicklook = [fp_quicklook]
    tools_mock.plot_coverage()


@patch("matplotlib.pyplot.show")
def test_plot_quicklook_alternative_filepaths(tools_mock):
    fp_quicklook = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    tools_mock.plot_coverage(filepaths=[fp_quicklook, fp_quicklook, fp_quicklook])


@patch("matplotlib.pyplot.show")
def test_plot_result(tools_mock):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.tif"
    tools_mock.result = [fp_tif]
    tools_mock.plot_results()


@patch("matplotlib.pyplot.show")
def test_plot_result_alternative_filepaths_and_titles(tools_mock):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.tif"
    tools_mock.plot_results(filepaths=[fp_tif, fp_tif, fp_tif], titles=["a", "b", "c"])


def test_get_blocks(tools_mock):
    with requests_mock.Mocker() as m:
        url_get_blocks = f"{tools_mock.auth._endpoint()}/blocks"
        m.get(
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


def test_plot_result_not_accepted_file_format_raises():
    filepaths = [Path("abc/123.hdf", "abc/123.json")]
    with pytest.raises(ValueError):
        Tools().plot_results(filepaths=filepaths)


@pytest.mark.live
def test_get_blocks_live(tools_live):
    blocks = tools_live.get_blocks(basic=False)
    assert isinstance(blocks, list)
    blocknames = [block["name"] for block in blocks]
    assert "tiling" in blocknames


def test_get_blocks_not_basic_dataframe(tools_mock):
    with requests_mock.Mocker() as m:
        url_get_blocks = f"{tools_mock.auth._endpoint()}/blocks"
        m.get(
            url=url_get_blocks,
            json={
                "data": [
                    {"id": "789-2736-212", "name": "tiling"},
                    {"id": "789-2736-212", "name": "sharpening"},
                ],
                "error": {},
            },
        )

        blocks_df = tools_mock.get_blocks(basic=False, as_dataframe=True)
    assert isinstance(blocks_df, pd.DataFrame)
    assert "tiling" in blocks_df["name"].to_list()


def test_get_block_details(tools_mock):
    block_id = "273612-13"
    with requests_mock.Mocker() as m:
        url_get_blocks_details = f"{tools_mock.auth._endpoint()}/blocks/{block_id}"
        m.get(
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


def test_validate_manifest(tools_mock):
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    with requests_mock.Mocker() as m:
        url_validate_mainfest = f"{tools_mock.auth._endpoint()}/validate-schema/block"
        m.post(
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
    with pytest.raises(ValueError):
        tools_live.validate_manifest(path_or_json=mainfest_json)
