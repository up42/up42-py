from pathlib import Path
import json
import tempfile

import requests_mock
import pytest
import geopandas as gpd

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    catalog_mock,
    catalog_live,
)
import up42  # pylint: disable=wrong-import-order


with open(
    Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_construct_parameters(catalog_mock):
    search_paramaters = catalog_mock.construct_parameters(
        geometry=mock_search_parameters["intersects"],
        start_date="2014-01-01",
        end_date="2016-12-31",
        sensors=["pleiades"],
        max_cloudcover=20,
        sortby="cloudCoverage",
        limit=4,
        ascending=False,
    )
    assert isinstance(search_paramaters, dict)
    assert search_paramaters["datetime"] == mock_search_parameters["datetime"]
    assert json.dumps(search_paramaters["intersects"]) == json.dumps(
        search_paramaters["intersects"]
    )
    assert search_paramaters["limit"] == mock_search_parameters["limit"]
    assert search_paramaters["query"] == mock_search_parameters["query"]
    assert search_paramaters["sortby"] == mock_search_parameters["sortby"]


def test_construct_parameters_unsopported_sensor_raises(catalog_mock):
    with pytest.raises(ValueError):
        catalog_mock.construct_parameters(
            geometry=mock_search_parameters["intersects"],
            sensors=["some_unspoorted_sensor"],
        )


def test_search(catalog_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_response.json"
    ) as json_file:
        json_search_response = json.load(json_file)

    with requests_mock.Mocker() as m:
        url_search = f"{catalog_mock.auth._endpoint()}/catalog/stac/search"
        m.post(
            url=url_search, json=json_search_response,
        )
        search_results = catalog_mock.search(mock_search_parameters)

    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (1, 10)


@pytest.mark.live
def test_search_live(catalog_live):
    search_results = catalog_live.search(mock_search_parameters)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (4, 10)
    assert list(search_results.columns) == [
        "index",
        "geometry",
        "id",
        "acquisitionDate",
        "constellation",
        "providerName",
        "blockNames",
        "cloudCoverage",
        "providerProperties",
        "scene_id",
    ]
    assert list(search_results.index) == list(range(search_results.shape[0]))

    # As fc
    search_results = catalog_live.search(mock_search_parameters, as_dataframe=False)
    assert isinstance(search_results, dict)
    assert search_results["type"] == "FeatureCollection"


def test_download_quicklook(catalog_mock):
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    with tempfile.TemporaryDirectory() as tempdir:
        provider = "oneatlas"
        with requests_mock.Mocker() as m:
            url = f"{catalog_mock.auth._endpoint()}/catalog/{provider}/image/{sel_id}/quicklook"
            quicklook_file = (
                Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
            )
            m.get(url, content=open(quicklook_file, "rb").read())

            out_paths = catalog_mock.download_quicklooks(
                [sel_id], output_directory=tempdir
            )

        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"


@pytest.mark.live
def test_download_quicklook_live(catalog_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_live.download_quicklooks(
            ["6dffb8be-c2ab-46e3-9c1c-6958a54e4527"], output_directory=tempdir
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"
