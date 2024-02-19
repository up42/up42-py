import json
import os
import tempfile
from pathlib import Path

import geopandas as gpd  # type: ignore
import pandas as pd
import pytest

from up42.catalog import Catalog
from up42.order import Order

from .fixtures.fixtures_globals import API_HOST, DATA_PRODUCT_ID, ORDER_ID, WORKSPACE_ID

with open(
    Path(__file__).resolve().parent / "mock_data/search_params_simple.json",
    encoding="utf-8",
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_get_collections(catalog_mock):
    collections = catalog_mock.get_collections()
    assert isinstance(collections, list)
    assert collections[0]["name"]


@pytest.mark.live
def test_get_collections_live(catalog_live):
    collections = catalog_live.get_collections()
    assert isinstance(collections, list)
    assert collections[0]["name"]


def test_get_data_product_schema(catalog_mock):
    data_product_schema = catalog_mock.get_data_product_schema(DATA_PRODUCT_ID)
    assert isinstance(data_product_schema, dict)
    assert data_product_schema["properties"]


@pytest.mark.live
def test_get_data_product_schema_live(catalog_live):
    data_product_schema = catalog_live.get_data_product_schema(os.getenv("TEST_UP42_DATA_PRODUCT_ID"))
    assert isinstance(data_product_schema, dict)
    assert data_product_schema["properties"]


def test_get_data_products_basic(catalog_mock):
    data_products_basic = catalog_mock.get_data_products()
    assert isinstance(data_products_basic, dict)
    basic_keys = {"data_products", "host", "collection"}
    assert basic_keys <= set(list(data_products_basic.values())[0].keys())
    assert "tasking_should_be_filtered_in_catalog_test" not in data_products_basic
    assert "test_not_integrated" not in data_products_basic
    assert len(data_products_basic) == 2


def test_get_data_products(catalog_mock):
    data_products = catalog_mock.get_data_products(basic=False)
    assert isinstance(data_products, list)
    assert data_products[0]["id"]

    for product in data_products:
        assert product["collection"]["title"] not in [
            "tasking_should_be_filtered_in_catalog_test",
            "test_not_integrated",
        ]
    assert len(data_products) == 2


@pytest.mark.live
def test_get_data_products_live(catalog_live):
    data_products = catalog_live.get_data_products(basic=False)
    assert isinstance(data_products, list)
    assert data_products[0]["id"]


def test_construct_search_parameters(catalog_mock):
    search_parameters = catalog_mock.construct_search_parameters(
        geometry=mock_search_parameters["intersects"],
        collections=["phr"],
        start_date="2014-01-01",
        end_date="2022-12-31",
        usage_type=["DATA", "ANALYTICS"],
        limit=4,
        max_cloudcover=20,
    )
    assert isinstance(search_parameters, dict)
    assert search_parameters["datetime"] == mock_search_parameters["datetime"]
    search_params_coords = {
        "type": search_parameters["intersects"]["type"],
        "coordinates": [
            [[float(coord[0]), float(coord[1])] for coord in search_parameters["intersects"]["coordinates"][0]]
        ],
    }
    assert search_params_coords == mock_search_parameters["intersects"]
    assert search_parameters["limit"] == mock_search_parameters["limit"]
    assert search_parameters["query"] == mock_search_parameters["query"]


def test_construct_search_parameters_fc_multiple_features_raises(catalog_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_footprints.geojson",
        encoding="utf-8",
    ) as json_file:
        fc = json.load(json_file)

    with pytest.raises(ValueError) as e:
        catalog_mock.construct_search_parameters(
            geometry=fc,
            start_date="2020-01-01",
            end_date="2020-08-10",
            collections=["phr"],
            limit=10,
            max_cloudcover=15,
        )
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry contains multiple geometries."


def test_search(catalog_mock):
    search_results = catalog_mock.search(mock_search_parameters)

    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (4, 15)


@pytest.mark.live
def test_search_live(catalog_live):
    search_results = catalog_live.search(mock_search_parameters)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape[0] != 0
    assert search_results.shape[1] > 10
    assert list(search_results.columns) == [
        "geometry",
        "id",
        "constellation",
        "collection",
        "providerName",
        "up42:usageType",
        "providerProperties",
        "sceneId",
        "producer",
        "acquisitionDate",
        "start_datetime",
        "end_datetime",
        "cloudCoverage",
        "resolution",
        "deliveryTime",
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
        search_parameters = catalog_usagetype_mock.construct_search_parameters(
            start_date="2014-01-01T00:00:00",
            end_date="2020-12-31T23:59:59",
            collections=["phr"],
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
    assert all(search_results["up42:usageType"].apply(lambda x: params["result1"] in x or params["result2"] in x))


@pytest.mark.skip(reason="Flaky catalog return")
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
    search_parameters = catalog_live.construct_search_parameters(
        start_date="2014-01-01T00:00:00",
        end_date="2020-12-31T23:59:59",
        collections=["phr"],
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
    assert all(search_results["up42:usageType"].apply(lambda x: result in x or result2 in x))


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
        "collections": ["phr", "spot"],
    }
    search_results = catalog_mock.search(search_params_limit_614)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (614, 15)


@pytest.mark.live
def test_search_catalog_pagination_live(catalog_live):
    search_params_limit_720 = {
        "datetime": "2018-01-01T00:00:00Z/2019-12-31T23:59:59Z",
        "collections": ["phr", "spot"],
        "bbox": [
            -125.859375,
            32.93492866908233,
            -116.82861328125001,
            41.65649719441145,
        ],
        "limit": 720,
    }
    search_results = catalog_live.search(search_params_limit_720)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (720, 15)
    assert search_results.collection.nunique() == 2
    assert all(search_results.collection.isin(["phr", "spot"]))
    period_column = pd.to_datetime(search_results.acquisitionDate, format="mixed")
    assert all(
        (period_column > pd.to_datetime("2018-01-01T00:00:00Z"))
        & (period_column <= pd.to_datetime("2019-12-31T23:59:59Z"))
    )


@pytest.mark.live
def test_search_catalog_pagination_no_results(catalog_live):
    """
    Sanity check that the pagination loop does not introduce undesired results.
    """
    search_params_no_results = {
        "datetime": "2018-01-01T00:00:00Z/2018-01-02T23:59:59Z",
        "collections": ["phr", "spot"],
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
        "limit": 10,
    }
    search_results = catalog_live.search(search_params_no_results)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.empty


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
        "collections": ["phr", "spot"],
    }
    search_results = catalog_pagination_mock.search(search_params_limit_614)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (550, 15)
    assert all(search_results.collection.isin(["phr", "spot"]))


def test_download_quicklook(catalog_mock, requests_mock):
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    host = "oneatlas"
    url_quicklooks = f"{API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklooks, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(image_ids=[sel_id], collection="phr", output_directory=tempdir)
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"


def test_download_no_quicklook(catalog_mock, requests_mock):
    sel_id = "dfc54412-8b9c-45a3-b46a-dd030a47c2f3"
    host = "oneatlas"
    url_quicklook = f"{API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    requests_mock.get(url_quicklook, status_code=404)

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(image_ids=[sel_id], collection="phr", output_directory=tempdir)
        assert len(out_paths) == 0


def test_download_1_quicklook_1_no_quicklook(catalog_mock, requests_mock):
    sel_id_no = "dfc54412-8b9c-45a3-b46a-dd030a47c2f3"
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    host = "oneatlas"
    url_no_quicklook = f"{API_HOST}/catalog/{host}/image/{sel_id_no}/quicklook"
    requests_mock.get(url_no_quicklook, status_code=404)

    url_quicklook = f"{API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklook, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(
            image_ids=[sel_id, sel_id_no],
            collection="phr",
            output_directory=tempdir,
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"


@pytest.mark.live
def test_download_quicklook_live(catalog_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_live.download_quicklooks(
            image_ids=["36f52f1f-6de1-4079-b116-5d1215091339"],
            collection="phr",
            output_directory=tempdir,
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"


def test_construct_order_parameters(catalog_mock):
    order_parameters = catalog_mock.construct_order_parameters(
        data_product_id=DATA_PRODUCT_ID,
        image_id="123",
        aoi=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


@pytest.mark.skip(reason="No live tests in the SDK.")
@pytest.mark.live
@pytest.mark.parametrize(
    "product_id",
    [
        ("613ad1f5-4148-4460-a316-1a97e46058f9"),
        ("83e21b35-e431-43a0-a1c4-22a6ad313911"),
        ("205fd9e1-4b00-4f0a-aabd-01e2f3f4dfba"),
        ("123eabab-0511-4f36-883a-80928716c3db"),
        ("07c33a51-94b9-4509-84df-e9c13ea92b84"),
        ("469f9b2f-1631-4c09-b66d-575abd41dc8f"),
        ("bd102407-1814-4f92-8b5a-7697b7a73f5a"),
        ("4f866cd3-d816-4c98-ace3-e6105623cf13"),
        ("28d4a077-6620-4ab5-9a03-c96bf622457e"),
        ("9d16c506-a6c0-4cf2-a020-8ecaf10b4160"),
        ("3a89d24e-515a-460f-a494-96be55da10a9"),
        ("47a693ba-4f8b-414d-8d5b-697373df4765"),
        ("9f790255-e8dc-4954-b5f9-3e7bea37cc69"),
        ("a6f64332-3148-4e05-a475-45a02176f210"),
    ],
)
def test_construct_order_parameters_live(catalog_live, product_id):
    order_parameters = catalog_live.construct_order_parameters(
        data_product_id=product_id,
        image_id="123",
        aoi=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


# pylint: disable=unused-argument
def test_estimate_order_from_catalog(catalog_order_parameters, requests_mock, auth_mock):
    catalog_instance = Catalog(auth=auth_mock)
    expected_payload = {
        "summary": {"totalCredits": 100, "totalSize": 0.1, "unit": "SQ_KM"},
        "results": [{"index": 0, "credits": 100, "unit": "SQ_KM", "size": 0.1}],
        "errors": [],
    }
    url_order_estimation = f"{API_HOST}/v2/orders/estimate"
    requests_mock.post(url=url_order_estimation, json=expected_payload)
    estimation = catalog_instance.estimate_order(catalog_order_parameters)
    assert isinstance(estimation, int)
    assert estimation == 100


def test_order_from_catalog(
    order_parameters,
    order_mock,
    catalog_mock,
    requests_mock,
):
    requests_mock.post(
        url=f"{API_HOST}/v2/orders?workspaceId={WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": ORDER_ID}],
            "errors": [],
        },
    )
    order = catalog_mock.place_order(order_parameters=order_parameters)
    assert isinstance(order, Order)
    assert order.order_id == ORDER_ID


def test_order_from_catalog_track_status(catalog_order_parameters, order_mock, catalog_mock, requests_mock):
    requests_mock.post(
        url=f"{API_HOST}/v2/orders?workspaceId={WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": ORDER_ID}],
            "errors": [],
        },
    )
    url_order_info = f"{API_HOST}/v2/orders/{order_mock.order_id}"
    requests_mock.get(
        url_order_info,
        [
            {"json": {"status": "PLACED"}},
            {"json": {"status": "BEING_FULFILLED"}},
            {"json": {"status": "FULFILLED"}},
        ],
    )
    order = catalog_mock.place_order(
        order_parameters=catalog_order_parameters,
        track_status=True,
        report_time=0.1,
    )
    assert isinstance(order, Order)
    assert order.order_id == ORDER_ID


@pytest.mark.live
def test_estimate_order_from_catalog_live(catalog_order_parameters, catalog_live):
    estimation = catalog_live.estimate_order(catalog_order_parameters)
    assert isinstance(estimation, int)
    assert estimation == 100


@pytest.mark.skip(reason="Placing orders costs credits.")
@pytest.mark.live
def test_order_from_catalog_live(catalog_order_parameters, catalog_live):
    order = catalog_live.place_order(catalog_order_parameters)
    assert isinstance(order, Order)
    assert order.order_id


def test_search_when_data_products_are_returned_as_list(catalog_mock):
    search_results = catalog_mock.search(mock_search_parameters, data_products_bool=False)
    assert isinstance(search_results, gpd.GeoDataFrame)
    assert search_results.shape == (4, 15)


def test_download_quicklook_something(catalog_mock, requests_mock):
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    host = "oneatlas"
    url_quicklooks = f"{API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklooks, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(
            image_ids=[sel_id], collection="phr", output_directory=tempdir, data_products_bool=False
        )
        assert len(out_paths) == 1
        assert Path(out_paths[0]).exists()
        assert Path(out_paths[0]).suffix == ".jpg"
