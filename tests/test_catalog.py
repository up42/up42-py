import pathlib
import uuid
from typing import List, Optional, cast

import geojson  # type: ignore
import geopandas as gpd  # type: ignore
import mock
import numpy as np
import pandas as pd
import pytest
import requests
import requests_mock as req_mock
import shapely  # type: ignore

from up42 import auth, catalog, glossary, order

from . import helpers
from .fixtures import fixtures_globals as constants

Geometry = catalog.Geometry

PHR = "phr"
SIMPLE_BOX = shapely.box(0, 0, 1, 1).__geo_interface__
START_DATE = "2014-01-01"
END_DATE = "2022-12-31"
DATE_RANGE = "2014-01-01T00:00:00Z/2022-12-31T23:59:59Z"
SEARCH_PARAMETERS = {
    "datetime": DATE_RANGE,
    "intersects": SIMPLE_BOX,
    "collections": [PHR],
    "limit": 10,
}
FEATURE = {
    "type": "Feature",
    "properties": {"some": "data"},
    "geometry": {"type": "Point", "coordinates": (1.0, 2.0)},
}
POINT_BBOX = (1.0, 2.0, 1.0, 2.0)


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth.session = requests.session()
        workspace_mock.id = constants.WORKSPACE_ID
        yield


@pytest.fixture(autouse=True)
def set_status_raising_session():
    session = requests.Session()
    session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
    glossary.ProductGlossary.session = session  # type: ignore
    catalog.CatalogBase.session = session  # type: ignore


class TestCatalogBase:
    @pytest.fixture(scope="class", params=["catalog", "tasking"])
    def order_parameters(self, request) -> order.OrderParams:
        geometry_key = "aoi" if request.param == "catalog" else "geometry"
        return {
            "dataProduct": "some-data-product",
            "params": {geometry_key: {"some": "shape"}},
        }

    def test_should_get_data_product_schema(self, auth_mock: auth.Auth, requests_mock: req_mock.Mocker):
        data_product_schema = {"schema": "some-schema"}
        url = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
        requests_mock.get(url=url, json=data_product_schema)
        catalog_obj = catalog.CatalogBase(auth_mock, constants.WORKSPACE_ID)
        assert catalog_obj.get_data_product_schema(constants.DATA_PRODUCT_ID) == data_product_schema

    def test_should_place_order(
        self, auth_mock: auth.Auth, requests_mock: req_mock.Mocker, order_parameters: order.OrderParams
    ):
        info = {"status": "SOME STATUS"}
        requests_mock.get(
            url=f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}",
            json=info,
        )
        requests_mock.post(
            url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
            json={"results": [{"id": constants.ORDER_ID}], "errors": []},
        )
        order_obj = catalog.CatalogBase(auth_mock, constants.WORKSPACE_ID).place_order(
            order_parameters=order_parameters
        )
        assert order_obj.order_id == constants.ORDER_ID

    @pytest.mark.parametrize(
        "info",
        [{"type": "ARCHIVE"}, {"type": "TASKING", "orderDetails": {"subStatus": "substatus"}}],
        ids=["ARCHIVE", "TASKING"],
    )
    def test_should_track_order_status(
        self, auth_mock: auth.Auth, requests_mock: req_mock.Mocker, info: dict, order_parameters: order.OrderParams
    ):
        requests_mock.post(
            url=f"{constants.API_HOST}/v2/orders?workspaceId={constants.WORKSPACE_ID}",
            json={"results": [{"id": constants.ORDER_ID}], "errors": []},
        )
        statuses = ["INITIAL STATUS", "PLACED", "BEING_FULFILLED", "FULFILLED"]
        responses = [{"json": {"status": status, **info}} for status in statuses]
        requests_mock.get(f"{constants.API_HOST}/v2/orders/{constants.ORDER_ID}", responses)
        order_obj = catalog.CatalogBase(auth_mock, constants.WORKSPACE_ID).place_order(
            order_parameters=order_parameters,
            track_status=True,
            report_time=0.1,
        )
        assert order_obj.order_id == constants.ORDER_ID
        assert order_obj.status == "FULFILLED"


class TestCatalog:
    host = "oneatlas"
    catalog = catalog.Catalog(auth=mock.MagicMock(), workspace_id=constants.WORKSPACE_ID)

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
        with pytest.raises(catalog.InvalidCollections, match=r"Selected collections \['unknown'\] are not valid.*"):
            self.catalog.search({"collections": ["unknown"]})

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
            self.catalog.search({"collections": ["collection1", "collection2"]})

    @pytest.mark.parametrize(
        "feature, expected_geom",
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
        ids=["with_features", "without_features"],
    )
    @pytest.mark.parametrize(
        "as_dataframe",
        [True, False],
        ids=["as_dataframe", "as_dict"],
    )
    @pytest.mark.usefixtures("product_glossary")
    def test_should_search(
        self, requests_mock: req_mock.Mocker, feature: dict, expected_geom: gpd.GeoDataFrame, as_dataframe: bool
    ):
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
            additional_matcher=helpers.match_request_body(SEARCH_PARAMETERS),
        )
        requests_mock.post(
            url=next_page_url,
            json=second_page,
            additional_matcher=helpers.match_request_body(SEARCH_PARAMETERS),
        )
        results = self.catalog.search(SEARCH_PARAMETERS, as_dataframe=as_dataframe)
        if as_dataframe:
            results = cast(gpd.GeoDataFrame, results)
            pd.testing.assert_frame_equal(results.drop(columns="geometry"), expected_geom.drop(columns="geometry"))
            assert results.geometry.equals(expected_geom.geometry)
            assert results.crs == expected_geom.crs
        else:
            bbox = results.pop("bbox")
            assert results == {
                "type": "FeatureCollection",
                "features": [
                    {**FEATURE, "id": "0", "bbox": POINT_BBOX},
                    {**FEATURE, "id": "1", "bbox": POINT_BBOX},
                ]
                if feature
                else [],
            }
            if feature:
                assert bbox == POINT_BBOX
            else:
                assert all(np.isnan(coor) for coor in bbox)

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

        out_paths = self.catalog.download_quicklooks(
            image_ids=[image_id, missing_image_id],
            collection=PHR,
            output_directory=output_directory,
        )
        download_folder: pathlib.Path = output_directory if output_directory else pathlib.Path.cwd() / "catalog"
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
        response = {**SEARCH_PARAMETERS}
        optional_response: dict = {"query": {}}
        if "max_cloudcover" in max_cloudcover:
            optional_response["query"]["cloudCoverage"] = {"lte": max_cloudcover["max_cloudcover"]}
        if "usage_type" in usage_type:
            optional_response["query"]["up42:usageType"] = {"in": usage_type["usage_type"]}
        response = {**response, **optional_response}
        assert self.catalog.construct_search_parameters(**params) == response

    def test_should_fail_construct_search_parameters_with_wrong_data_usage(self):
        with pytest.raises(catalog.InvalidUsageType, match="usage_type is invalid"):
            self.catalog.construct_search_parameters(
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
        auth_mock: mock.MagicMock,
        requests_mock: req_mock.Mocker,
        aoi: Optional[Geometry],
        tags: Optional[List[str]],
    ):
        schema_property = "any-property"
        image_id = str(uuid.uuid4())
        url_schema = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
        requests_mock.get(
            url_schema,
            json={
                "required": [schema_property],
                "properties": {schema_property: {"type": "string", "title": "string", "format": "string"}},
            },
        )
        order_parameters: order.OrderParams = catalog.Catalog(
            auth_mock, constants.WORKSPACE_ID
        ).construct_order_parameters(
            data_product_id=constants.DATA_PRODUCT_ID,
            image_id=image_id,
            aoi=aoi,
            tags=tags,
        )
        assert schema_property in order_parameters["params"]
        assert order_parameters["params"]["id"] == image_id
        assert order_parameters["dataProduct"] == constants.DATA_PRODUCT_ID
        if tags is not None:
            assert order_parameters["tags"] == tags
        if aoi is not None:
            assert order_parameters["params"]["aoi"] == aoi

    def test_estimate_order_from_catalog(
        self,
        auth_mock: mock.MagicMock,
        requests_mock: req_mock.Mocker,
        catalog_order_parameters: order.OrderParams,
    ):
        order_estimate_url = f"{constants.API_HOST}/v2/orders/estimate"
        expected_credits = 100
        requests_mock.post(
            url=order_estimate_url,
            json={
                "summary": {"totalCredits": expected_credits},
                "errors": [],
            },
        )
        catalog_obj = catalog.Catalog(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
        assert catalog_obj.estimate_order(catalog_order_parameters) == expected_credits
