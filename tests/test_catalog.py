from pathlib import Path
import json
import tempfile

import pytest
import geopandas as gpd

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    catalog_mock,
    catalog_live,
)


with open(
    Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_construct_parameters(catalog_mock):
    search_parameters = catalog_mock.construct_parameters(
        geometry=mock_search_parameters["intersects"],
        start_date="2014-01-01",
        end_date="2016-12-31",
        sensors=["pleiades", "spot", "sentinel1"],
        max_cloudcover=20,
        sortby="cloudCoverage",
        limit=4,
        ascending=False,
    )
    assert isinstance(search_parameters, dict)
    assert search_parameters["datetime"] == mock_search_parameters["datetime"]
    assert json.dumps(search_parameters["intersects"]) == json.dumps(
        search_parameters["intersects"]
    )
    assert search_parameters["limit"] == mock_search_parameters["limit"]
    assert search_parameters["query"] == mock_search_parameters["query"]
    assert search_parameters["sortby"] == mock_search_parameters["sortby"]


def test_construct_parameters_fc_multiple_non_overlapping_features(catalog_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_footprints.geojson"
    ) as json_file:
        fc = json.load(json_file)

    search_parameters = catalog_mock.construct_parameters(
        geometry=fc,
        start_date="2020-01-01",
        end_date="2020-08-10",
        sensors=["sentinel2"],
        limit=10,
        max_cloudcover=15,
        sortby="acquisitionDate",
        ascending=True,
    )
    assert isinstance(search_parameters, dict)
    assert search_parameters["datetime"] == "2020-01-01T00:00:00Z/2020-08-10T23:59:59Z"
    assert search_parameters["intersects"]["type"] == "MultiPolygon"


def test_construct_parameters_unsopported_sensor_raises(catalog_mock):
    with pytest.raises(ValueError):
        catalog_mock.construct_parameters(
            geometry=mock_search_parameters["intersects"],
            sensors=["some_unspoorted_sensor"],
        )


def test_search(catalog_mock, requests_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_response.json"
    ) as json_file:
        json_search_response = json.load(json_file)
    url_search = f"{catalog_mock.auth._endpoint()}/catalog/stac/search"
    requests_mock.post(
        url=url_search,
        json=json_search_response,
    )
    search_results = catalog_mock.search(mock_search_parameters)

    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (1, 9)


@pytest.mark.live
def test_search_live(catalog_live):
    search_results = catalog_live.search(mock_search_parameters)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (4, 10)
    assert list(search_results.columns) == [
        "geometry",
        "id",
        "acquisitionDate",
        "constellation",
        "providerName",
        "blockNames",
        "cloudCoverage",
        "up42:usageType",
        "providerProperties",
        "scene_id",
    ]
    assert list(search_results.index) == list(range(search_results.shape[0]))

    # As fc
    search_results = catalog_live.search(mock_search_parameters, as_dataframe=False)
    assert isinstance(search_results, dict)
    assert search_results["type"] == "FeatureCollection"


def test_download_quicklook(catalog_mock, requests_mock):
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    provider = "oneatlas"
    url_quicklooks = (
        f"{catalog_mock.auth._endpoint()}/catalog/{provider}/image/{sel_id}/quicklook"
    )
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklooks, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(
            image_ids=[sel_id], sensor="pleiades", output_directory=tempdir
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"


def test_download_no_quicklook(catalog_mock, requests_mock):
    sel_id = "dfc54412-8b9c-45a3-b46a-dd030a47c2f3"
    provider = "sobloo-image"
    url_quicklook = (
        f"{catalog_mock.auth._endpoint()}/catalog/{provider}/image/{sel_id}/quicklook"
    )
    requests_mock.get(url_quicklook, status_code=404)

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(
            image_ids=[sel_id], sensor="sentinel5p", output_directory=tempdir
        )
        assert len(out_paths) == 0


def test_download_1_quicklook_1_no_quicklook(catalog_mock, requests_mock):
    sel_id_no = "dfc54412-8b9c-45a3-b46a-dd030a47c2f3"
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    provider = "sobloo-image"
    url_no_quicklook = f"{catalog_mock.auth._endpoint()}/catalog/{provider}/image/{sel_id_no}/quicklook"
    requests_mock.get(url_no_quicklook, status_code=404)

    url_quicklook = (
        f"{catalog_mock.auth._endpoint()}/catalog/{provider}/image/{sel_id}/quicklook"
    )
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklook, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(
            image_ids=[sel_id, sel_id_no],
            sensor="sentinel5p",
            output_directory=tempdir,
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"


@pytest.mark.live
def test_download_quicklook_live(catalog_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_live.download_quicklooks(
            image_ids=["6dffb8be-c2ab-46e3-9c1c-6958a54e4527"],
            sensor="pleiades",
            output_directory=tempdir,
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"
