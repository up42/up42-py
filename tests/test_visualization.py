import json
from pathlib import Path
import warnings

import pytest
import geopandas as gpd
from mock import patch
import pandas as pd
import rasterio
import folium
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

from .context import (
    folium_base_map,
)


def test_folium_base_map():
    m = folium_base_map()
    assert isinstance(m, folium.Map)
    assert m.crs == "EPSG3857"


poly = Polygon([(0, 0), (1, 1), (1, 0)])


@patch("matplotlib.pyplot.show")
def test_plot_result(tools_mock):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.tif"
    tools_mock.result = [fp_tif]
    tools_mock.plot_results()


@patch("matplotlib.pyplot.show")
def test_plot_result_alternative_filepaths_and_titles(tools_mock):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.tif"
    tools_mock.plot_results(filepaths=[fp_tif, fp_tif, fp_tif], titles=["a", "b", "c"])


def test_plot_result_not_accepted_file_format_raises():
    filepaths = [Path("abc/123.hdf", "abc/123.json")]
    with pytest.raises(ValueError):
        Tools().plot_results(filepaths=filepaths)


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