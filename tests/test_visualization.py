from pathlib import Path
import tarfile
from shutil import copyfile

import pytest
import geopandas as gpd
from mock import patch
import pandas as pd
import folium
from shapely import wkt
from folium import Map

from .context import folium_base_map, VizTools

# pylint: disable=unused-import,wrong-import-order
from .fixtures import auth_mock, job_mock


# pylint: disable=unused-argument


def test_folium_base_map():
    m = folium_base_map()
    assert isinstance(m, folium.Map)
    assert m.crs == "EPSG3857"


@patch("matplotlib.pyplot.show")
def test_plot_result_job(capture_canvas, job_mock):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.jpg"
    job_mock.results = [fp_tif]
    job_mock.plot_results(plot_file_format=[".jpg"])


@patch("matplotlib.pyplot.show")
def test_plot_result_alternative_filepaths_and_titles(capture_canvas):
    fp_tif = Path(__file__).resolve().parent / "mock_data/s2_128.jpg"
    VizTools().plot_results(
        filepaths=[fp_tif, fp_tif, fp_tif],
        titles=["a", "b", "c"],
        plot_file_format=[".jpg"],
    )


def test_plot_result_not_accepted_file_format_raises():
    filepaths = [Path("abc/123.hdf", "abc/123.json")]
    with pytest.raises(ValueError):
        VizTools().plot_results(filepaths=filepaths)


@patch("matplotlib.pyplot.show")
def test_plot_quicklooks(capture_canvas, job_mock):
    fp_quicklooks = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    job_mock.quicklooks = [fp_quicklooks]
    job_mock.plot_quicklooks()


@patch("matplotlib.pyplot.show")
def test_plot_quicklooks_alternative_filepaths(capture_canvas):
    fp_quicklook = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    VizTools().plot_quicklooks(filepaths=[fp_quicklook, fp_quicklook, fp_quicklook])


@patch("matplotlib.pyplot.show")
def test_plot_coverage(capture_canvas):
    df = gpd.read_file(
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson",
        as_dataframe=True,
    )
    VizTools().plot_coverage(df)


@patch("matplotlib.pyplot.show")
def test_plot_coverage_wrong_legend_column_ignores(capture_canvas):
    df = gpd.read_file(
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson",
        as_dataframe=True,
    )
    VizTools().plot_coverage(df, legend_column="abcdefgh")


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

    m = VizTools()._map_images(plot_file_format, gdf, filepaths)
    m._repr_html_()
    # Render does not return an object but an html document, as expected
    # Disabling pylint to avoid error
    out = m._parent.render()  # pylint: disable=assignment-from-no-return

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

    m = VizTools()._map_images(plot_file_format, gdf, filepaths, name_column="nikoo")
    m._repr_html_()
    out = m._parent.render()  # pylint: disable=assignment-from-no-return

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

    m = VizTools()._map_images(plot_file_format, gdf, filepaths)
    m._repr_html_()
    out = m._parent.render()  # pylint: disable=assignment-from-no-return

    assert "Image 1 - 2a581680-17e4-4a61-8aa9-9e47e1bf36bb" in out


def test_map_results(job_mock):
    fp_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with tarfile.open(fp_tgz) as tar:
        tar.extractall(fp_tgz.parent)
    fp_tif = (
        fp_tgz.parent
        / "output/7e17f023-a8e3-43bd-aaac-5bbef749c7f4/7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif"
    )
    fp_data_json = fp_tgz.parent / "output/data.json"

    job_mock.results = [str(fp_tif), str(fp_data_json)]
    map_object = job_mock.map_results()
    assert isinstance(map_object, Map)


def test_map_results_additional_geojson(job_mock):
    fp_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with tarfile.open(fp_tgz) as tar:
        tar.extractall(fp_tgz.parent)
    fp_tif = (
        fp_tgz.parent
        / "output/7e17f023-a8e3-43bd-aaac-5bbef749c7f4/7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif"
    )
    fp_data_json = fp_tgz.parent / "output/data.json"
    fp_data_geojson = fp_tgz.parent / "output/additional_vector_file.geojson"
    copyfile(fp_data_json, fp_data_geojson)

    job_mock.results = [str(fp_tif), str(fp_data_json), str(fp_data_geojson)]
    map_object = job_mock.map_results()
    assert isinstance(map_object, Map)
