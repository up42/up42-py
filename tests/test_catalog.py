import json
import pathlib
import tempfile
from unittest import mock

import geopandas as gpd  # type: ignore
import pytest

from up42 import catalog, order

from .fixtures import fixtures_globals as constants

with open(
    pathlib.Path(__file__).resolve().parent / "mock_data/search_params_simple.json",
    encoding="utf-8",
) as json_file:
    mock_search_parameters = json.load(json_file)


@pytest.fixture(autouse=True)
def mock_workspace_id():
    with mock.patch("up42.main.workspace") as mock_workspace:
        mock_workspace.id = constants.WORKSPACE_ID
        yield


def test_get_collections(catalog_mock):
    collections = catalog_mock.get_collections()
    assert isinstance(collections, list)
    assert collections[0]["name"]


def test_get_data_product_schema(catalog_mock):
    data_product_schema = catalog_mock.get_data_product_schema(constants.DATA_PRODUCT_ID)
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
        pathlib.Path(__file__).resolve().parent / "mock_data/search_footprints.geojson",
        encoding="utf-8",
    ) as file:
        fc = json.load(file)

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


def test_search_usagetype(catalog_usagetype_mock):
    """
    Result & Result2 are one of the combinations of
    "DATA" and "ANALYTICS". Result2 can be None.

    Test is not pytest-paramterized as the same
    catalog_usagetype_mock needs be used for
    each iteration.

    The result assertion needs to allow multiple combinations,
    e.g. when searching for ["DATA", "ANALYTICS"],
    the result can be ["DATA"], ["ANALYTICS"]
    or ["DATA", "ANALYTICS"].
    """
    params1 = {"usage_type": ["DATA"], "result1": "DATA", "result2": ""}
    params2 = {
        "usage_type": ["ANALYTICS"],
        "result1": "ANALYTICS",
        "result2": "",
    }
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


def test_search_catalog_pagination_exhausted(catalog_pagination_mock):
    """
    Search results pagination is exhausted after 1 extra page (50 elements),
    resulting in only 500+50 features even though
    the limit parameter asked for 614.
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
    url_quicklooks = f"{constants.API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    quicklook_file = pathlib.Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklooks, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(image_ids=[sel_id], collection="phr", output_directory=tempdir)
        assert len(out_paths) == 1
        assert pathlib.Path(out_paths[0]).exists()
        assert pathlib.Path(out_paths[0]).suffix == ".jpg"


def test_download_no_quicklook(catalog_mock, requests_mock):
    sel_id = "dfc54412-8b9c-45a3-b46a-dd030a47c2f3"
    host = "oneatlas"
    url_quicklook = f"{constants.API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    requests_mock.get(url_quicklook, status_code=404)

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(image_ids=[sel_id], collection="phr", output_directory=tempdir)
        assert len(out_paths) == 0


def test_download_1_quicklook_1_no_quicklook(catalog_mock, requests_mock):
    sel_id_no = "dfc54412-8b9c-45a3-b46a-dd030a47c2f3"
    sel_id = "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
    host = "oneatlas"
    url_no_quicklook = f"{constants.API_HOST}/catalog/{host}/image/{sel_id_no}/quicklook"
    requests_mock.get(url_no_quicklook, status_code=404)

    url_quicklook = f"{constants.API_HOST}/catalog/{host}/image/{sel_id}/quicklook"
    quicklook_file = pathlib.Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url_quicklook, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        out_paths = catalog_mock.download_quicklooks(
            image_ids=[sel_id, sel_id_no],
            collection="phr",
            output_directory=tempdir,
        )
        assert len(out_paths) == 1
        assert pathlib.Path(out_paths[0]).exists()
        assert pathlib.Path(out_paths[0]).suffix == ".jpg"


def test_construct_order_parameters(catalog_mock):
    order_parameters = catalog_mock.construct_order_parameters(
        data_product_id=constants.DATA_PRODUCT_ID,
        image_id="123",
        aoi=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


# pylint: disable=unused-argument
def test_estimate_order_from_catalog(catalog_order_parameters, requests_mock, auth_mock):
    catalog_instance = catalog.Catalog(auth=auth_mock)
    expected_payload = {
        "summary": {"totalCredits": 100, "totalSize": 0.1, "unit": "SQ_KM"},
        "results": [{"index": 0, "credits": 100, "unit": "SQ_KM", "size": 0.1}],
        "errors": [],
    }
    url_order_estimation = f"{constants.API_HOST}/v2/orders/estimate"
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
        url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": constants.ORDER_ID}],
            "errors": [],
        },
    )
    placed_order = catalog_mock.place_order(order_parameters=order_parameters)
    assert isinstance(placed_order, order.Order)
    assert placed_order.order_id == constants.ORDER_ID


def test_order_from_catalog_track_status(catalog_order_parameters, order_mock, catalog_mock, requests_mock):
    requests_mock.post(
        url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
        json={
            "results": [{"index": 0, "id": constants.ORDER_ID}],
            "errors": [],
        },
    )
    url_order_info = f"{constants.API_HOST}/v2/orders/{order_mock.order_id}"
    requests_mock.get(
        url_order_info,
        [
            {"json": {"status": "PLACED"}},
            {"json": {"status": "BEING_FULFILLED"}},
            {"json": {"status": "FULFILLED"}},
        ],
    )
    placed_order = catalog_mock.place_order(
        order_parameters=catalog_order_parameters,
        track_status=True,
        report_time=0.1,
    )
    assert isinstance(placed_order, order.Order)
    assert placed_order.order_id == constants.ORDER_ID
