import pathlib
import uuid
from typing import List, Optional, cast

import geojson  # type: ignore
import geopandas as gpd  # type: ignore
import mock
import pandas as pd
import pytest
import requests_mock as req_mock
import shapely  # type: ignore

from tests import constants, helpers
from up42 import catalog, glossary, order

PHR = "phr"
SIMPLE_BOX = shapely.box(0, 0, 1, 1).__geo_interface__
START_DATE = "2014-01-01"
END_DATE = "2022-12-31"
DATE_RANGE = "2014-01-01T00:00:00Z/2022-12-31T23:59:59Z"
FEATURE = {
    "type": "Feature",
    "properties": {"some": "data"},
    "geometry": {"type": "Point", "coordinates": (1.0, 2.0)},
}
POINT_BBOX = (1.0, 2.0, 1.0, 2.0)


class TestCatalogBase:
    @pytest.fixture(scope="class", params=["catalog", "tasking"])
    def order_parameters(self, request) -> order.OrderParams:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    @pytest.mark.parametrize("collection_type", list(glossary.CollectionType))
    def test_should_get_data_product_schema(
        self,
        requests_mock: req_mock.Mocker,
        collection_type: glossary.CollectionType,
    ) -> None:
        data_product_schema = {"schema": "some-schema"}
        url = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
        requests_mock.get(url=url, json=data_product_schema)
        catalog_obj = catalog.CatalogBase(collection_type)
        assert catalog_obj.get_data_product_schema(constants.DATA_PRODUCT_ID) == data_product_schema

    @pytest.mark.parametrize("collection_type", list(glossary.CollectionType))
    def test_should_estimate_order(
        self,
        requests_mock: req_mock.Mocker,
        order_parameters: order.OrderParams,
        collection_type: glossary.CollectionType,
    ):
        catalog_obj = catalog.CatalogBase(collection_type)
        expected_payload = {
            "summary": {"totalCredits": 100, "totalSize": 0.1, "unit": "SQ_KM"},
            "results": [{"index": 0, "credits": 100, "unit": "SQ_KM", "size": 0.1}],
            "errors": [],
        }
        url_order_estimation = f"{constants.API_HOST}/v2/orders/estimate"
        requests_mock.post(url=url_order_estimation, json=expected_payload)
        assert catalog_obj.estimate_order(order_parameters) == 100

    @pytest.mark.parametrize("collection_type", list(glossary.CollectionType))
    def test_should_place_order(
        self,
        order_parameters: order.OrderParams,
        collection_type: glossary.CollectionType,
    ):
        with mock.patch("up42.order.Order.place") as place_order:
            place_order.return_value = mock.sentinel
            assert catalog.CatalogBase(collection_type).place_order(order_parameters=order_parameters) == mock.sentinel
            place_order.assert_called_with(order_parameters, constants.WORKSPACE_ID)

    @pytest.mark.parametrize("collection_type", list(glossary.CollectionType))
    def test_should_track_order_status(
        self,
        order_parameters: order.OrderParams,
        collection_type: glossary.CollectionType,
    ):
        order_obj = mock.MagicMock()
        with mock.patch("up42.order.Order.place") as place_order:
            place_order.return_value = order_obj
            assert (
                catalog.CatalogBase(collection_type).place_order(
                    order_parameters=order_parameters,
                    track_status=True,
                    report_time=0.1,
                )
                == order_obj
            )
            place_order.assert_called_with(order_parameters, constants.WORKSPACE_ID)
            order_obj.track.assert_called_with(0.1)


class TestCatalog:
    host = "oneatlas"
    catalog_obj = catalog.Catalog()

    @pytest.fixture(params=["output_dir", "no_output_dir"])
    def output_directory(self, request, tmp_path) -> Optional[pathlib.Path]:
        return tmp_path if request.param == "output_dir" else None

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
                        "description": "collection",
                        "integrations": [],
                        "name": PHR,
                        "providers": [
                            {
                                "name": self.host,
                                "title": "provider-title",
                                "description": "provider",
                                "roles": ["PRODUCER", "HOST"],
                            }
                        ],
                        "dataProducts": [],
                    }
                ],
                "totalPages": 1,
            },
        )

    @pytest.mark.usefixtures("product_glossary")
    def test_search_fails_if_host_is_not_found(self):
        collection_name = "unknown"
        with pytest.raises(catalog.InvalidCollections, match=rf".*{collection_name}.*"):
            self.catalog_obj.search({"collections": [collection_name]})

    def test_search_fails_if_collections_hosted_by_different_hosts(self, requests_mock: req_mock.Mocker):
        collections_url = f"{constants.API_HOST}/v2/collections"
        requests_mock.get(
            collections_url,
            json={
                "content": [
                    {
                        "type": "ARCHIVE",
                        "title": f"title{idx}",
                        "name": f"collection{idx}",
                        "description": "collection",
                        "integrations": [],
                        "dataProducts": [],
                        "providers": [
                            {
                                "name": f"host{idx}",
                                "title": "provider-title",
                                "description": "provider",
                                "roles": ["HOST"],
                            }
                        ],
                    }
                    for idx in [1, 2]
                ],
                "totalPages": 1,
            },
        )
        with pytest.raises(catalog.MultipleHosts):
            self.catalog_obj.search({"collections": ["collection1", "collection2"]})

    @pytest.mark.parametrize(
        "feature, expected_df",
        [
            (
                FEATURE,
                gpd.GeoDataFrame.from_features(
                    geojson.FeatureCollection(
                        features=[
                            {**FEATURE, "id": "0", "bbox": POINT_BBOX},
                            {**FEATURE, "id": "1", "bbox": POINT_BBOX},
                        ]
                    ),
                    crs="EPSG:4326",
                ),
            ),
            (None, gpd.GeoDataFrame(columns=["geometry"], geometry="geometry")),
        ],
        ids=["response_with_features", "response_without_features"],
    )
    @pytest.mark.parametrize(
        "as_dataframe",
        [True, False],
        ids=["as_dataframe", "as_dict"],
    )
    @pytest.mark.parametrize(
        "limit",
        [{}, {"limit": 10}],
        ids=["with_limit", "without_limit"],
    )
    @pytest.mark.usefixtures("product_glossary")
    def test_should_search(
        self,
        requests_mock: req_mock.Mocker,
        feature: Optional[dict],
        expected_df: gpd.GeoDataFrame,
        as_dataframe: bool,
        limit: dict,
    ):
        search_params = {
            "datetime": DATE_RANGE,
            "intersects": SIMPLE_BOX,
            "collections": [PHR],
        }
        search_params.update(limit)
        search_url = f"{constants.API_HOST}/catalog/hosts/{self.host}/stac/search"
        next_page_url = f"{search_url}/next"
        features = []
        if feature:
            features.append(feature)
        first_page = {
            "type": "FeatureCollection",
            "features": features,
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
            additional_matcher=helpers.match_request_body(search_params),
        )
        requests_mock.post(
            url=next_page_url,
            json=second_page,
            additional_matcher=helpers.match_request_body(search_params),
        )
        results = self.catalog_obj.search(search_params, as_dataframe=as_dataframe)
        if as_dataframe:
            results = cast(gpd.GeoDataFrame, results)
            pd.testing.assert_frame_equal(results, expected_df)
        else:
            columns = {} if feature else {"columns": ["geometry"]}
            pd.testing.assert_frame_equal(gpd.GeoDataFrame.from_features(results, **columns), expected_df)

    @pytest.mark.usefixtures("product_glossary")
    def test_should_download_available_quicklooks(
        self, requests_mock: req_mock.Mocker, output_directory: Optional[pathlib.Path]
    ):
        missing_image_id = "missing-image-id"
        image_id = "image-id"
        missing_quicklook_url = f"{constants.API_HOST}/catalog/{self.host}/image/{missing_image_id}/quicklook"
        requests_mock.get(missing_quicklook_url, status_code=404)

        quicklook_url = f"{constants.API_HOST}/catalog/{self.host}/image/{image_id}/quicklook"
        quicklook_file = pathlib.Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
        requests_mock.get(quicklook_url, content=quicklook_file.read_bytes())

        out_paths = self.catalog_obj.download_quicklooks(
            image_ids=[image_id, missing_image_id],
            collection=PHR,
            output_directory=output_directory,
        )
        download_folder = output_directory or pathlib.Path.cwd() / "catalog"
        assert out_paths == [str(download_folder / f"quicklook_{image_id}.jpg")]

    @pytest.mark.parametrize(
        "usage_type",
        [
            {"usage_type": ["DATA"]},
            {"usage_type": ["ANALYTICS"]},
            {"usage_type": ["DATA", "ANALYTICS"]},
            {},
        ],
        ids=[
            "usage_type:DATA",
            "usage_type:ANALYTICS",
            "usage_type:DATA, ANALYTICS",
            "usage_type:None",
        ],
    )
    @pytest.mark.parametrize(
        "max_cloudcover",
        [
            {"max_cloudcover": 100},
            {},
        ],
        ids=[
            "max_cloudcover:100",
            "max_cloudcover:None",
        ],
    )
    def test_should_construct_search_parameters(self, usage_type: dict, max_cloudcover: dict):
        params = {
            "geometry": SIMPLE_BOX,
            "collections": [PHR],
            "start_date": START_DATE,
            "end_date": END_DATE,
            **usage_type,
            **max_cloudcover,
        }
        query = {}
        if max_cloudcover:
            query["cloudCoverage"] = {"lte": max_cloudcover["max_cloudcover"]}
        if usage_type:
            query["up42:usageType"] = {"in": usage_type["usage_type"]}
        expected_params = {
            "datetime": DATE_RANGE,
            "intersects": SIMPLE_BOX,
            "collections": [PHR],
            "limit": 10,
            "query": query,
        }
        assert self.catalog_obj.construct_search_parameters(**params) == expected_params

    def test_fails_to_construct_search_parameters_with_wrong_data_usage(self):
        with pytest.raises(catalog.InvalidUsageType, match="usage_type is invalid"):
            self.catalog_obj.construct_search_parameters(
                geometry=SIMPLE_BOX,
                collections=[PHR],
                start_date=START_DATE,
                end_date=END_DATE,
                usage_type=["WRONG_TYPE"],  # type: ignore
            )

    @pytest.mark.parametrize(
        "aoi",
        [
            SIMPLE_BOX,
            None,
        ],
        ids=[
            "aoi:SIMPLE_BOX",
            "aoi:None",
        ],
    )
    @pytest.mark.parametrize(
        "tags",
        [
            ["tag"],
            None,
        ],
        ids=[
            "tags:Value",
            "tags:None",
        ],
    )
    def test_should_construct_order_parameters(
        self,
        requests_mock: req_mock.Mocker,
        aoi: Optional[catalog.Geometry],
        tags: Optional[List[str]],
    ):
        required_property = "any-property"
        image_id = str(uuid.uuid4())
        url_schema = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
        requests_mock.get(
            url_schema,
            json={
                "required": [required_property],
                "properties": {
                    required_property: {
                        "type": "string",
                        "title": "string",
                        "format": "string",
                    }
                },
            },
        )
        order_parameters = catalog.Catalog().construct_order_parameters(
            data_product_id=constants.DATA_PRODUCT_ID,
            image_id=image_id,
            aoi=aoi,
            tags=tags,
        )
        expected = {
            "params": {
                "id": image_id,
                required_property: None,
                **({"aoi": aoi} if aoi else {}),
            },
            "dataProduct": constants.DATA_PRODUCT_ID,
            **({"tags": tags} if tags else {}),
        }
        assert order_parameters == expected
