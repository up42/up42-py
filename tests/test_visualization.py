import json
from pathlib import Path
import warnings

import pytest
import geopandas as gpd
from mock import patch
import pandas as pd
import rasterio
import folium
from shapely import wkt
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


def test_map_images_2_scenes():
    plot_file_format = [".jpg"]

    result_csv = Path(__file__).resolve().parent / "mock_data/df_2scenes.csv"
    result_df = pd.read_csv(result_csv)
    result_df["geometry"] = result_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(result_df, geometry="geometry")

    quicklook_1 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_16e18e15-c941-4aae-97cd-d67b18dc9f6e.jpg"
    )
    quicklook_2 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_f8c03432-cec1-41b7-a203-4d871a03290f.jpg"
    )
    filepaths = [quicklook_1, quicklook_2]

    m = Visualization()._map_images(plot_file_format, gdf, filepaths)
    m._repr_html_()
    out = m._parent.render()

    assert "Image 1 - f8c03432-cec1-41b7-a203-4d871a03290f" in out
    assert "Image 2 - 16e18e15-c941-4aae-97cd-d67b18dc9f6e" in out


def test_map_images_2_scenes_no_column_name():
    plot_file_format = [".jpg"]

    result_csv = Path(__file__).resolve().parent / "mock_data/df_2scenes.csv"
    result_df = pd.read_csv(result_csv)
    result_df["geometry"] = result_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(result_df, geometry="geometry")

    quicklook_1 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_16e18e15-c941-4aae-97cd-d67b18dc9f6e.jpg"
    )
    quicklook_2 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_f8c03432-cec1-41b7-a203-4d871a03290f.jpg"
    )
    filepaths = [quicklook_1, quicklook_2]

    m = Visualization()._map_images(plot_file_format, gdf, filepaths, name_column="nikoo")
    m._repr_html_()
    out = m._parent.render()

    assert "Image 1 - " in out
    assert "Image 2 - " in out


def test_map_images_1_scene():
    plot_file_format = [".jpg"]

    result_csv = Path(__file__).resolve().parent / "mock_data/df_1scene.csv"
    result_df = pd.read_csv(result_csv)
    result_df["geometry"] = result_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(result_df, geometry="geometry")

    quicklook = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_16e18e15-c941-4aae-97cd-d67b18dc9f6e.jpg"
    )
    filepaths = [quicklook]

    m = Visualization()._map_images(plot_file_format, gdf, filepaths)
    m._repr_html_()
    out = m._parent.render()

    assert "Image 1 - 2a581680-17e4-4a61-8aa9-9e47e1bf36bb" in out
