import json
import pathlib
import uuid

import geopandas as gpd  # type: ignore
import mock
import pytest
import requests
import requests_mock as req_mock

from up42 import catalog, order
from .fixtures import fixtures_globals as constants

with open(
    pathlib.Path(__file__).resolve().parent / "mock_data/search_params_simple.json",
    encoding="utf-8",
) as json_file:
    mock_search_parameters = json.load(json_file)


@pytest.fixture(autouse=True)
def set_status_raising_session():
    session = requests.Session()
    session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
    catalog.ProductGlossary.session = session  # type: ignore
    catalog.CatalogBase.session = session  # type: ignore


class TestProductGlossary:
    @pytest.mark.parametrize("collection_type", ["ARCHIVE", "TASKING"])
    def test_should_get_collections(self, requests_mock: req_mock.Mocker, collection_type: catalog.CollectionType):
        url = f"{constants.API_HOST}/collections?is_integrated=true&paginated=false"
        target_collection = {"type": collection_type}
        ignored_collection = {"type": "other_type"}
        requests_mock.get(url, json={"data": [target_collection, ignored_collection]})
        assert catalog.ProductGlossary.get_collections(collection_type) == [target_collection]

    @pytest.mark.parametrize("collection_type", ["ARCHIVE", "TASKING"])
    def test_get_data_products_grouped(self, requests_mock: req_mock.Mocker, collection_type: catalog.CollectionType):
        url = f"{constants.API_HOST}/data-products?is_integrated=true&paginated=false"
        requests_mock.get(
            url,
            json={
                "data": [
                    *[
                        {
                            "id": idx,
                            "collection": {
                                "type": collection_type,
                                "title": "title",
                                "name": "name",
                                "host": {"name": "host_name"},
                            },
                            "productConfiguration": {"title": f"config{idx}"},
                        }
                        for idx in [1, 2]
                    ],
                    {
                        "id": 3,
                        "collection": {
                            "type": "other_type",
                        },
                    },
                ]
            },
        )
        assert catalog.ProductGlossary.get_data_products(collection_type, grouped=True) == {
            "title": {
                "collection": "name",
                "host": "host_name",
                "data_products": {"config1": 1, "config2": 2},
            }
        }

    @pytest.mark.parametrize("collection_type", ["ARCHIVE", "TASKING"])
    def test_should_get_data_products(self, requests_mock: req_mock.Mocker, collection_type: catalog.CollectionType):
        url = f"{constants.API_HOST}/data-products?is_integrated=true&paginated=false"
        target_product = {"collection": {"type": collection_type}}
        ignored_product = {"collection": {"type": "other_type"}}
        requests_mock.get(url, json={"data": [target_product, ignored_product]})
        assert catalog.ProductGlossary.get_data_products(collection_type, grouped=False) == [target_product]


def test_get_data_product_schema(catalog_mock):
    data_product_schema = catalog_mock.get_data_product_schema(constants.DATA_PRODUCT_ID)
    assert isinstance(data_product_schema, dict)
    assert data_product_schema["properties"]


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


class TestCatalog:
    def test_should_search(self, requests_mock: req_mock.Mocker):
        host = "oneatlas"
        collection = "phr"
        data_products_url = f"{constants.API_HOST}/data-products?is_integrated=true&paginated=false"
        requests_mock.get(
            data_products_url,
            json={
                "data": [
                    {
                        "id": "id",
                        "collection": {
                            "type": "ARCHIVE",
                            "title": "title",
                            "name": collection,
                            "host": {"name": host},
                        },
                        "productConfiguration": {"title": "config"},
                    }
                ]
            },
        )

        search_url = f"{constants.API_HOST}/catalog/hosts/oneatlas/stac/search"
        next_page_url = f"{search_url}/next"
        bbox = (1.0, 2.0, 1.0, 2.0)
        feature = {
            "type": "Feature",
            "properties": {
                "some": "data",
            },
            "geometry": {"type": "Point", "coordinates": (1.0, 2.0)},
        }
        first_page = {
            "type": "FeatureCollection",
            "features": [feature],
            "links": [
                {
                    "rel": "next",
                    "href": next_page_url,
                }
            ],
        }
        second_page = {**first_page, "links": []}
        requests_mock.post(url=search_url, json=first_page)
        requests_mock.post(url=next_page_url, json=second_page)

        results = catalog.Catalog(auth=mock.MagicMock(), workspace_id=constants.WORKSPACE_ID).search(
            mock_search_parameters
        )

        assert isinstance(results, gpd.GeoDataFrame)
        assert results.__geo_interface__ == {
            "type": "FeatureCollection",
            "features": [
                {**feature, "id": "0", "bbox": bbox},
                {**feature, "id": "1", "bbox": bbox},
            ],
            "bbox": bbox,
        }

    def test_search_usagetype(self):
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
            search_parameters = catalog.Catalog(
                auth=mock.MagicMock(), workspace_id=constants.WORKSPACE_ID
            ).construct_search_parameters(
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
            del search_parameters

    def test_should_download_available_quicklooks(self, requests_mock: req_mock.Mocker, tmp_path):
        missing_image_id = str(uuid.uuid4())
        image_id = str(uuid.uuid4())
        host = "oneatlas"
        collection = "phr"
        data_products_url = f"{constants.API_HOST}/data-products?is_integrated=true&paginated=false"
        requests_mock.get(
            data_products_url,
            json={
                "data": [
                    {
                        "id": "id",
                        "collection": {
                            "type": "ARCHIVE",
                            "title": "title",
                            "name": collection,
                            "host": {"name": host},
                        },
                        "productConfiguration": {"title": "config"},
                    }
                ]
            },
        )

        missing_quicklook_url = f"{constants.API_HOST}/catalog/{host}/image/{missing_image_id}/quicklook"
        requests_mock.get(missing_quicklook_url, status_code=404)

        quicklook_url = f"{constants.API_HOST}/catalog/{host}/image/{image_id}/quicklook"
        quicklook_file = pathlib.Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
        requests_mock.get(quicklook_url, content=quicklook_file.read_bytes())

        out_paths = catalog.Catalog(auth=mock.MagicMock(), workspace_id=constants.WORKSPACE_ID).download_quicklooks(
            image_ids=[image_id, missing_image_id],
            collection=collection,
            output_directory=tmp_path,
        )
        assert out_paths == [str(tmp_path / f"quicklook_{image_id}.jpg")]
        assert requests_mock.call_count == 3


def test_construct_order_parameters(catalog_mock):
    order_parameters = catalog_mock.construct_order_parameters(
        data_product_id=constants.DATA_PRODUCT_ID,
        image_id="123",
        aoi=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


def test_estimate_order_from_catalog(catalog_order_parameters, requests_mock, auth_mock):
    catalog_instance = catalog.Catalog(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
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
    order_mock,  # pylint: disable=unused-argument
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
