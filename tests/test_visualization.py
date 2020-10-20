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

from .context import folium_base_map, Visualization


def test_folium_base_map():
    m = folium_base_map()
    assert isinstance(m, folium.Map)
    assert m.crs == "EPSG3857"


@patch("matplotlib.pyplot.show")
def test_plot_result_job(jobs_mock):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.tif"
    jobs_mock.result = [fp_tif]
    jobs_mock.plot_results()


@patch("matplotlib.pyplot.show")
def test_plot_result_alternative_filepaths_and_titles(capture_canvas):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.jpg"
    Visualization().plot_results(
        filepaths=[fp_tif, fp_tif, fp_tif],
        titles=["a", "b", "c"],
        plot_file_format=[".jpg"],
    )


def test_plot_result_not_accepted_file_format_raises():
    filepaths = [Path("abc/123.hdf", "abc/123.json")]
    with pytest.raises(ValueError):
        Visualization().plot_results(filepaths=filepaths)


@patch("matplotlib.pyplot.show")
def test_plot_quicklooks(jobs_mock):
    fp_quicklook = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    jobs_mock.quicklook = [fp_quicklook]
    jobs_mock.plot_quicklooks()


@patch("matplotlib.pyplot.show")
def test_plot_quicklooks_alternative_filepaths(capture_canvas):
    fp_quicklook = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    Visualization().plot_quicklooks(
        filepaths=[fp_quicklook, fp_quicklook, fp_quicklook]
    )


@patch("matplotlib.pyplot.show")
def test_plot_coverage(capture_canvas):
    df = gpd.read_file(
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson",
        as_dataframe=True,
    )
    Visualization().plot_coverage(df)


@patch("matplotlib.pyplot.show")
def test_plot_coverage_wrong_legend_column_ignores(capture_canvas):
    df = gpd.read_file(
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson",
        as_dataframe=True,
    )
    Visualization().plot_coverage(df, legend_column="abcdefgh")
