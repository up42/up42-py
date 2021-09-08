from pathlib import Path
import json
import tempfile

import pytest
import geopandas as gpd

from .context import Order

# pylint: disable=unused-import
from .test_order import order_payload
from .fixtures import (
    auth_mock,
    auth_live,
    catalog_mock,
    catalog_live,
    catalog_pagination_mock,
    catalog_usagetype_mock,
    order_mock,
    ORDER_ID,
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


def test_search(catalog_mock):
    search_results = catalog_mock.search(mock_search_parameters)

    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (4, 14)


@pytest.mark.live
def test_search_live(catalog_live):
    search_results = catalog_live.search(mock_search_parameters)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (4, 14)
    assert list(search_results.columns) == [
        "geometry",
        "id",
        "acquisitionDate",
        "constellation",
        "collection",
        "providerName",
        "blockNames",
        "cloudCoverage",
        "up42:usageType",
        "providerProperties",
        "sceneId",
        "resolution",
        "deliveryTime",
        "producer",
    ]
    assert list(search_results.index) == list(range(search_results.shape[0]))

    # As fc
    search_results = catalog_live.search(mock_search_parameters, as_dataframe=False)
    assert isinstance(search_results, dict)
    assert search_results["type"] == "FeatureCollection"


def test_search_usagetype(catalog_usagetype_mock):
    """
    Result & Result2 are one of the combinations of "DATA" and "ANALYTICS". Result2 can
    be None.

    Test is not pytest-paramterized as the same catalog_usagetype_mock needs be used for
    each iteration.

    The result assertion needs to allow multiple combinations, e.g. when searching for
    ["DATA", "ANALYTICS"], the result can be ["DATA"], ["ANALYTICS"] or ["DATA", "ANALYTICS"].
    """
    params1 = {"usage_type": ["DATA"], "result1": "DATA", "result2": ""}
    params2 = {"usage_type": ["ANALYTICS"], "result1": "ANALYTICS", "result2": ""}
    params3 = {
        "usage_type": ["DATA", "ANALYTICS"],
        "result1": "DATA",
        "result2": "ANALYTICS",
    }

    for params in [params1, params2, params3]:
        search_parameters = catalog_usagetype_mock.construct_parameters(
            start_date="2014-01-01T00:00:00",
            end_date="2020-12-31T23:59:59",
            limit=1,
            usage_type=params["usage_type"],
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [13.375966, 52.515068],
                        [13.375966, 52.516639],
                        [13.378314, 52.516639],
                        [13.378314, 52.515068],
                        [13.375966, 52.515068],
                    ]
                ],
            },
        )

    search_results = catalog_usagetype_mock.search(search_parameters, as_dataframe=True)
    assert all(
        search_results["up42:usageType"].apply(
            lambda x: params["result1"] in x or params["result2"] in x
        )
    )


@pytest.mark.live
@pytest.mark.parametrize(
    "usage_type,result,result2",
    [
        (["DATA"], "DATA", ""),
        (["ANALYTICS"], "ANALYTICS", ""),
        (["DATA", "ANALYTICS"], "DATA", "ANALYTICS"),
    ],
)
def test_search_usagetype_live(catalog_live, usage_type, result, result2):
    """
    Result & Result2 are one of the combinations of "DATA" and "ANALYTICS". Result2 can
    be None.

    The result assertion needs to allow multiple combinations, e.g. when searching for
    ["DATA", "ANALYTICS"], the result can be ["DATA"], ["ANALYTICS"] or ["DATA", "ANALYTICS"].
    """
    search_parameters = catalog_live.construct_parameters(
        start_date="2014-01-01T00:00:00",
        end_date="2020-12-31T23:59:59",
        limit=100,
        usage_type=usage_type,
        geometry={
            "type": "Polygon",
            "coordinates": [
                [
                    [13.375966, 52.515068],
                    [13.375966, 52.516639],
                    [13.378314, 52.516639],
                    [13.378314, 52.515068],
                    [13.375966, 52.515068],
                ]
            ],
        },
    )

    search_results = catalog_live.search(search_parameters, as_dataframe=True)
    assert all(
        search_results["up42:usageType"].apply(lambda x: result in x or result2 in x)
    )


def test_search_catalog_pagination(catalog_mock):
    search_params_limit_614 = {
        "datetime": "2014-01-01T00:00:00Z/2020-01-20T23:59:59Z",
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [12.008056640625, 52.66305767075935],
                    [16.292724609375, 52.66305767075935],
                    [16.292724609375, 52.72963909783717],
                    [12.008056640625, 52.72963909783717],
                    [12.008056640625, 52.66305767075935],
                ]
            ],
        },
        "limit": 614,
        "query": {
            "dataBlock": {
                "in": [
                    "oneatlas-pleiades-fullscene",
                    "oneatlas-pleiades-display",
                    "oneatlas-pleiades-aoiclipped",
                    "oneatlas-spot-fullscene",
                    "oneatlas-spot-display",
                    "oneatlas-spot-aoiclipped",
                ]
            }
        },
    }
    search_results = catalog_mock.search(search_params_limit_614)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (614, 14)


@pytest.mark.live
def test_search_catalog_pagination_live(catalog_live):
    search_params_limit_614 = {
        "datetime": "2014-01-01T00:00:00Z/2020-01-20T23:59:59Z",
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [12.008056640625, 52.66305767075935],
                    [16.292724609375, 52.66305767075935],
                    [16.292724609375, 52.72963909783717],
                    [12.008056640625, 52.72963909783717],
                    [12.008056640625, 52.66305767075935],
                ]
            ],
        },
        "limit": 614,
        "query": {
            "dataBlock": {
                "in": [
                    "oneatlas-pleiades-fullscene",
                    "oneatlas-pleiades-display",
                    "oneatlas-pleiades-aoiclipped",
                    "oneatlas-spot-fullscene",
                    "oneatlas-spot-display",
                    "oneatlas-spot-aoiclipped",
                ]
            }
        },
    }
    search_results = catalog_live.search(search_params_limit_614)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (614, 14)


def test_search_catalog_pagination_exhausted(catalog_pagination_mock):
    """
    Search results pagination is exhausted after 1 extra page (50 elements),
    resulting in only 500+50 features even though the limit parameter asked for 614.
    """
    search_params_limit_614 = {
        "datetime": "2014-01-01T00:00:00Z/2020-01-20T23:59:59Z",
        "intersects": {
            "type": "Polygon",
            "coordinates": [
                [
                    [12.008056640625, 52.66305767075935],
                    [16.292724609375, 52.66305767075935],
                    [16.292724609375, 52.72963909783717],
                    [12.008056640625, 52.72963909783717],
                    [12.008056640625, 52.66305767075935],
                ]
            ],
        },
        "limit": 614,
        "query": {
            "dataBlock": {
                "in": [
                    "oneatlas-pleiades-fullscene",
                    "oneatlas-pleiades-display",
                    "oneatlas-pleiades-aoiclipped",
                    "oneatlas-spot-fullscene",
                    "oneatlas-spot-display",
                    "oneatlas-spot-aoiclipped",
                ]
            }
        },
    }
    search_results = catalog_pagination_mock.search(search_params_limit_614)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (550, 14)


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


# pylint: disable=unused-argument
def test_estimate_order_from_catalog(
    order_payload, order_mock, catalog_mock, requests_mock
):
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
    url_order_estimation = (
        f"{catalog_mock.auth._endpoint()}/workspaces/"
        f"{catalog_mock.auth.workspace_id}/orders/estimate"
    )
    requests_mock.post(url=url_order_estimation, json={"data": {"credits": 100}})
    estimation = catalog_mock.estimate_order(
        order_payload["orderParams"]["aoi"], search_results.loc[0]
    )
    assert isinstance(estimation, int)
    assert estimation == 100


def test_order_from_catalog(order_payload, order_mock, catalog_mock, requests_mock):
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

    requests_mock.post(
        url=f"{catalog_mock.auth._endpoint()}/workspaces/{catalog_mock.auth.workspace_id}/orders",
        json={
            "data": {"id": ORDER_ID},
            "error": {},
        },
    )
    order = catalog_mock.place_order(
        order_payload["orderParams"]["aoi"], search_results.loc[0]
    )
    assert isinstance(order, Order)
    assert order.order_id == ORDER_ID


def test_order_from_catalog_track_status(
    order_payload, order_mock, catalog_mock, requests_mock
):
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

    requests_mock.post(
        url=f"{catalog_mock.auth._endpoint()}/workspaces/{catalog_mock.auth.workspace_id}/orders",
        json={
            "data": {"id": ORDER_ID},
            "error": {},
        },
    )
    url_order_info = (
        f"{order_mock.auth._endpoint()}/workspaces/"
        f"{order_mock.workspace_id}/orders/{order_mock.order_id}"
    )
    requests_mock.get(
        url_order_info,
        [
            {"json": {"data": {"status": "PLACED"}, "error": {}}},
            {"json": {"data": {"status": "BEING_FULFILLED"}, "error": {}}},
            {"json": {"data": {"status": "FULFILLED"}, "error": {}}},
        ],
    )
    order = catalog_mock.place_order(
        order_payload["orderParams"]["aoi"],
        search_results.loc[0],
        track_status=True,
        report_time=0.1,
    )
    assert isinstance(order, Order)
    assert order.order_id == ORDER_ID


@pytest.mark.live
def test_estimate_order_from_catalog_live(catalog_live):
    search_results = catalog_live.search(mock_search_parameters)
    estimation = catalog_live.estimate_order(
        mock_search_parameters["intersects"], search_results.loc[0]
    )
    assert isinstance(estimation, int)
    assert estimation == 12


@pytest.mark.skip(reason="Placing orders costs credits.")
@pytest.mark.live
def test_order_from_catalog_live(
    order_payload, order_mock, catalog_mock, requests_mock
):
    search_results = catalog_live.search(mock_search_parameters)
    order = catalog_live.place_order(
        mock_search_parameters["intersects"], search_results.loc[0]
    )
    assert isinstance(order, Order)
    assert order.order_id
