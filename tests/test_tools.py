import json
import os
from pathlib import Path

import pytest
import geopandas as gpd
from mock import patch

from .fixtures import (
    auth_mock,
    tools_mock,
    auth_live,
    tools_live,
)  # pylint: disable=unused-import
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
    tools_mock.quicklook = [fp_quicklook, fp_quicklook, fp_quicklook]
    tools_mock.plot_coverage()


# @patch("matplotlib.pyplot.show")
# def test_plot_result(tools_mock):
#     out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
#     out_tgz_file = open(out_tgz, "rb")
#
#     tools_mock.quicklook = [fp_quicklook]
#     tools_mock.plot_coverage()


@pytest.mark.live
def test_validate_manifest_valid(tools_live):
    _location_ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    fp = Path(_location_) / "mock_data/manifest.json"
    result = tools_live.validate_manifest(path_or_json=fp)
    assert result == {"valid": True, "errors": []}


@pytest.mark.live
def test_validate_manifest_invalid(tools_live):
    _location_ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    fp = Path(_location_) / "mock_data/manifest.json"
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


def test_plot_result_not_accepted_file_format_raises():
    filepaths = [Path("abc/123.hdf", "abc/123.json")]
    with pytest.raises(ValueError):
        Tools().plot_result(filepaths=filepaths)
