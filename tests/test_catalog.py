import copy
import json
import pathlib
import urllib.parse
from typing import Any, Optional

import geopandas as gpd  # type: ignore
import mock
import pytest
import requests
import requests_mock as req_mock
import shapely  # type: ignore

from up42 import catalog, order, utils

from . import helpers
from .fixtures import fixtures_globals as constants

PHR = "phr"
SIMPLE_BOX = shapely.box(0, 0, 1, 1).__geo_interface__
SEARCH_PARAMETERS = {
    "datetime": "2014-01-01T00:00:00Z/2022-12-31T23:59:59Z",
    "intersects": SIMPLE_BOX,
    "collections": [PHR],
    "limit": 4,
    "query": {
        "cloudCoverage": {"lte": 20},
        "up42:usageType": {"in": ["DATA", "ANALYTICS"]},
    },
}
COLLECTION_NAME = "pneo"
COLLECTION_TITLE = "Pléiades Neo"
COLLECTION_DESCRIPTION = "Very high resolution 30 cm optical satellite imagery"
COLLECTION_INTEGRATIONS = ["ACCESS_APPROVAL_REQUIRED", "FEASIBILITY_MAY_BE_REQUIRED"]
COLLECTION_PROVIDERS = [
    {
        "name": "oneatlas",
        "title": "OneAtlas",
        "description": "OneAtlas.",
        "roles": ["PRODUCER", "HOST"],
    }
]
COLLECTION_DATAPRODUCTS = [
    {
        "name": "pneo-analytic",
        "title": "Analytic",
        "description": "A reflectance product that was radiometrically corrected",
    }
]
COLLECTION_METADATA = {
    "name": COLLECTION_NAME,
    "title": COLLECTION_TITLE,
    "description": COLLECTION_DESCRIPTION,
    "integrations": COLLECTION_INTEGRATIONS,
    "providers": COLLECTION_PROVIDERS,
    "dataProducts": COLLECTION_DATAPRODUCTS,
}


@pytest.fixture(autouse=True)
def set_status_raising_session():
    session = requests.Session()
    session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
    catalog.ProductGlossary.session = session  # type: ignore
    catalog.CatalogBase.session = session  # type: ignore


class TestProductGlossary:
    @pytest.mark.parametrize("collection_type", [None, "ARCHIVE", "TASKING"])
    @pytest.mark.parametrize("only_non_commercial", [None, True, False])
    @pytest.mark.parametrize("sort_by", [None, str(utils.SortingField("createdAt", ascending=False))])
    def test_should_get_collections(
        self,
        requests_mock: req_mock.Mocker,
        collection_type: str,
        only_non_commercial: bool,
        sort_by: Optional[utils.SortingField],
    ):
        target_type = collection_type if collection_type is not None else "ARCHIVE"
        other_type = "TASKING" if target_type == "ARCHIVE" else "ARCHIVE"
        collection_test = catalog.Collection(
            name=COLLECTION_NAME,
            title=COLLECTION_TITLE,
            type=catalog.CollectionType(target_type),
            description=COLLECTION_DESCRIPTION,
            integrations=[catalog.IntegrationValue(integration) for integration in COLLECTION_INTEGRATIONS],
            providers=[catalog.Provider(**provider) for provider in COLLECTION_PROVIDERS],  # type: ignore[arg-type]
            data_products=[
                catalog.DataProduct(
                    id=data_product.get("id", None),
                    name=data_product["name"],
                    title=data_product["title"],
                    description=data_product["description"],
                    eula_id=data_product.get("eulaId", None),
                )
                for data_product in COLLECTION_DATAPRODUCTS
            ],
        )
        other_collection = catalog.Collection(
            name=COLLECTION_NAME,
            title=COLLECTION_TITLE,
            type=catalog.CollectionType(other_type),
            description=COLLECTION_DESCRIPTION,
            integrations=[catalog.IntegrationValue(integration) for integration in COLLECTION_INTEGRATIONS],
            providers=[catalog.Provider(**provider) for provider in COLLECTION_PROVIDERS],  # type: ignore[arg-type]
            data_products=[
                catalog.DataProduct(
                    id=data_product.get("id", None),
                    name=data_product["name"],
                    title=data_product["title"],
                    description=data_product["description"],
                    eula_id=data_product.get("eulaId", None),
                )
                for data_product in COLLECTION_DATAPRODUCTS
            ],
        )
        target_collection = copy.deepcopy(COLLECTION_METADATA)
        target_collection["type"] = target_type
        ignored_collection = copy.deepcopy(target_collection)
        ignored_collection["type"] = other_type
        query_params: dict[str, Any] = {}
        if only_non_commercial:
            query_params["onlyNonCommercial"] = ("true" if only_non_commercial else "false",)
        if sort_by:
            query_params["sort"] = str(sort_by)
        query_params["page"] = 0

        query = urllib.parse.urlencode(query_params, doseq=True)
        base_url = f"{constants.API_HOST}/v2/collections"
        requests_mock.get(
            url=base_url + (query and f"?{query}"),
            json={
                "content": [target_collection, ignored_collection] * 3,
                "totalPages": 2,
            },
        )

        query_params["page"] = "1"
        query = urllib.parse.urlencode(query_params, doseq=True)
        requests_mock.get(
            url=base_url + (query and f"?{query}"),
            json={
                "content": [target_collection, ignored_collection] * 2,
                "totalPages": 2,
            },
        )

        query_params["page"] = "2"
        query = urllib.parse.urlencode(query_params, doseq=True)
        requests_mock.get(
            url=base_url + (query and f"?{query}"),
            json={
                "content": [],
                "totalPages": 2,
            },
        )
        expected_collection = (
            [collection_test]
            if collection_type is not None
            else [collection_test, other_collection]  # type: ignore[list-item]
        )
        assert (
            list(
                catalog.ProductGlossary.get_collections(
                    collection_type=catalog.CollectionType(collection_type) if collection_type is not None else None,
                    only_non_commercial=only_non_commercial,
                    sortby=sort_by,
                )
            )
            == expected_collection * 5
        )


def test_get_data_product_schema(catalog_mock):
    data_product_schema = catalog_mock.get_data_product_schema(constants.DATA_PRODUCT_ID)
    assert isinstance(data_product_schema, dict)
    assert data_product_schema["properties"]


class TestCatalog:
    host = "oneatlas"
    catalog = catalog.Catalog(auth=mock.MagicMock(), workspace_id=constants.WORKSPACE_ID)

    @pytest.fixture
    def product_glossary(self, requests_mock: req_mock.Mocker):
        collections_url = f"{constants.API_HOST}/v2/collections"
        requests_mock.get(
            collections_url,
            json={
                "content": [
                    {
                        "type": "ARCHIVE",
                        "title": "title",
                        "description": COLLECTION_DESCRIPTION,
                        "integrations": COLLECTION_INTEGRATIONS,
                        "name": PHR,
                        "providers": [
                            {
                                "name": self.host,
                                "title": "provider title",
                                "description": "test",
                                "roles": ["PRODUCER", "HOST"],
                            }
                        ],
                        "dataProducts": COLLECTION_DATAPRODUCTS,
                    }
                ],
                "totalPages": 1,
            },
        )

    @pytest.mark.usefixtures("product_glossary")
    def test_search_fails_if_host_is_not_found(self):
        with pytest.raises(ValueError, match=r"Selected collections \['unknown'\] are not valid.*"):
            self.catalog.search({"collections": ["unknown"]})

    def test_search_fails_if_collections_hosted_by_different_hosts(self, requests_mock: req_mock.Mocker):
        data_products_url = f"{constants.API_HOST}/v2/collections"
        requests_mock.get(
            data_products_url,
            json={
                "content": [
                    {
                        "type": "ARCHIVE",
                        "title": f"title{idx}",
                        "name": f"collection{idx}",
                        "description": COLLECTION_DESCRIPTION,
                        "integrations": COLLECTION_INTEGRATIONS,
                        "dataProducts": COLLECTION_DATAPRODUCTS,
                        "providers": [
                            {"name": f"host{idx}", "title": "provider title", "description": "test", "roles": ["HOST"]}
                        ],
                    }
                    for idx in [1, 2]
                ],
                "totalPages": 1,
            },
        )
        with pytest.raises(ValueError):
            self.catalog.search({"collections": ["collection1", "collection2"]})

    @pytest.mark.usefixtures("product_glossary")
    def test_should_search(self, requests_mock: req_mock.Mocker):
        search_url = f"{constants.API_HOST}/catalog/hosts/{self.host}/stac/search"
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
        requests_mock.post(
            url=search_url,
            json=first_page,
            additional_matcher=helpers.match_request_body(SEARCH_PARAMETERS),
        )
        requests_mock.post(
            url=next_page_url,
            json=second_page,
            additional_matcher=helpers.match_request_body(SEARCH_PARAMETERS),
        )

        results = self.catalog.search(SEARCH_PARAMETERS)

        assert isinstance(results, gpd.GeoDataFrame)
        assert results.__geo_interface__ == {
            "type": "FeatureCollection",
            "features": [
                {**feature, "id": "0", "bbox": bbox},
                {**feature, "id": "1", "bbox": bbox},
            ],
            "bbox": bbox,
        }

    @pytest.mark.usefixtures("product_glossary")
    def test_should_download_available_quicklooks(self, requests_mock: req_mock.Mocker, tmp_path):
        missing_image_id = "missing-image-id"
        image_id = "image-id"
        missing_quicklook_url = f"{constants.API_HOST}/catalog/{self.host}/image/{missing_image_id}/quicklook"
        requests_mock.get(missing_quicklook_url, status_code=404)

        quicklook_url = f"{constants.API_HOST}/catalog/{self.host}/image/{image_id}/quicklook"
        quicklook_file = pathlib.Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
        requests_mock.get(quicklook_url, content=quicklook_file.read_bytes())

        out_paths = self.catalog.download_quicklooks(
            image_ids=[image_id, missing_image_id],
            collection=PHR,
            output_directory=tmp_path,
        )
        assert out_paths == [str(tmp_path / f"quicklook_{image_id}.jpg")]


def test_construct_search_parameters(catalog_mock):
    assert (
        catalog_mock.construct_search_parameters(
            geometry=SIMPLE_BOX,
            collections=[PHR],
            start_date="2014-01-01",
            end_date="2022-12-31",
            usage_type=["DATA", "ANALYTICS"],
            limit=4,
            max_cloudcover=20,
        )
        == SEARCH_PARAMETERS
    )


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
            collections=[PHR],
            limit=10,
            max_cloudcover=15,
        )
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry contains multiple geometries."


def test_construct_order_parameters(catalog_mock):
    order_parameters = catalog_mock.construct_order_parameters(
        data_product_id=constants.DATA_PRODUCT_ID,
        image_id="123",
        aoi=SIMPLE_BOX,
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


def test_search_usagetype(catalog_mock):
    """
    Result & Result2 are one of the combinations of
    "DATA" and "ANALYTICS". Result2 can be None.

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
        assert catalog_mock.construct_search_parameters(
            start_date="2014-01-01T00:00:00",
            end_date="2020-12-31T23:59:59",
            collections=[PHR],
            limit=1,
            usage_type=params["usage_type"],
            geometry=SIMPLE_BOX,
        ) == {
            "datetime": "2014-01-01T00:00:00Z/2020-12-31T23:59:59Z",
            "intersects": SIMPLE_BOX,
            "limit": 1,
            "collections": [PHR],
            "query": {"up42:usageType": {"in": params["usage_type"]}},
        }


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
