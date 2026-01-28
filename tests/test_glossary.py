import dataclasses
from typing import Any

import geojson  # type: ignore
import pytest
import requests
import requests_mock as req_mock

from tests import constants, helpers
from up42 import glossary, utils

DATA_PRODUCT = glossary.DataProduct(
    name="data-product-name",
    title="data-product-title",
    description="data-product",
    id="data-product-id",
    eula_id="eula-id",
)
RESOLUTION_VALUE = glossary.ResolutionValue(minimum=0.0, maximum=1.0)
INTEGRATION_VALUES: list[glossary.IntegrationValue] = [
    "ACCESS_APPROVAL_REQUIRED",
    "SAMPLE_DATA_AVAILABLE",
    "MANUAL_REQUEST_REQUIRED",
    "FEASIBILITY_STUDY_REQUIRED",
    "FEASIBILITY_STUDY_MAY_BE_REQUIRED",
    "QUOTATION_REQUIRED",
    "PRICE_ESTIMATION_AVAILABLE",
    "SEARCH_AVAILABLE",
    "THUMBNAIL_AVAILABLE",
    "QUICKLOOK_AVAILABLE",
]
COLLECTION_METADATA = glossary.CollectionMetadata(
    product_type="OPTICAL",
    resolution_class="VERY_HIGH",
    resolution_value=RESOLUTION_VALUE,
)
COLLECTION = glossary.Collection(
    name="collection-name",
    title="collection-title",
    description="collection",
    type=glossary.CollectionType.ARCHIVE,
    integrations=INTEGRATION_VALUES,
    providers=[
        glossary.Provider(
            name="provider-name",
            title="provider-title",
            description="provider",
            roles=["PRODUCER", "HOST"],
        )
    ],
    data_products=[DATA_PRODUCT],
    metadata=COLLECTION_METADATA,
)
BBOX = [0.0] * 4
POLYGON = {
    "type": "Polygon",
    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
}
SCENE_ID = "scene-id"
HOST_NAME = "host-name"
SCENE = glossary.Scene(
    bbox=BBOX,
    geometry=POLYGON,
    id=SCENE_ID,
    datetime="datetime",
    start_datetime="start-datetime",
    end_datetime="end-datetime",
    constellation="constellation",
    collection="collection",
    cloud_coverage=0.5,
    resolution=0.3,
    delivery_time="HOURS",
    producer="producer",
    quicklook=utils.ImageFile(
        url=f"{constants.API_HOST}/catalog/{HOST_NAME}/image/{SCENE_ID}/quicklook",
        file_name=f"quicklook_{SCENE_ID}.jpg",
    ),
    provider_properties={"some": "properties"},
)
SCENE_FEATURE = {
    "geometry": POLYGON,
    "bbox": BBOX,
    "properties": {
        "id": SCENE.id,
        "datetime": SCENE.datetime,
        "start_datetime": SCENE.start_datetime,
        "end_datetime": SCENE.end_datetime,
        "constellation": SCENE.constellation,
        "collection": SCENE.collection,
        "cloudCoverage": SCENE.cloud_coverage,
        "resolution": SCENE.resolution,
        "deliveryTime": SCENE.delivery_time,
        "producer": SCENE.producer,
        "providerProperties": SCENE.provider_properties,
    },
}


class TestDataProduct:
    data_product = glossary.DataProduct(
        name="name",
        title="title",
        description="description",
        id=constants.DATA_PRODUCT_ID,
        eula_id="eula-id",
    )

    def test_should_provide_no_schema_if_missing_id(self):
        assert not dataclasses.replace(self.data_product, id=None).schema

    def test_should_provide_schema(self, requests_mock: req_mock.Mocker) -> None:
        schema = {"schema": "some-schema"}
        url = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
        requests_mock.get(url=url, json=schema)
        assert self.data_product.schema == schema


class TestProvider:
    provider = glossary.Provider(
        name=HOST_NAME,
        title="title",
        description="description",
        roles=["PRODUCER", "HOST"],
    )
    search_url = f"{constants.API_HOST}/catalog/hosts/{HOST_NAME}/stac/search"

    @pytest.mark.parametrize(
        "provider, is_host",
        [
            (provider, True),
            (dataclasses.replace(provider, roles=["PRODUCER"]), False),
            (dataclasses.replace(provider, roles=["HOST"]), True),
        ],
    )
    def test_should_compute_whether_provider_is_host(self, provider, is_host: bool) -> None:
        assert provider.is_host == is_host

    def test_fails_to_search_if_provider_is_not_host(self):
        with pytest.raises(glossary.InvalidHost):
            next(dataclasses.replace(self.provider, roles=["PRODUCER"]).search())

    def test_fails_to_search_if_search_request_is_invalid(self, requests_mock: req_mock.Mocker):
        error_message = "invalid request"
        requests_mock.post(
            url=self.search_url,
            status_code=422,
            json={
                "data": {},
                "error": {"code": 422, "message": error_message, "details": "ignored"},
            },
        )
        with pytest.raises(glossary.InvalidSearchRequest, match=error_message):
            next(self.provider.search())

    @pytest.mark.parametrize("error_code", [400, 401, 403, 500])
    def test_should_propagate_search_failures(self, error_code: int, requests_mock: req_mock.Mocker):
        requests_mock.post(
            url=self.search_url,
            status_code=error_code,
        )
        with pytest.raises(requests.HTTPError):
            next(self.provider.search())

    @pytest.mark.parametrize("bbox", [None, BBOX])
    @pytest.mark.parametrize("intersects", [None, POLYGON])
    @pytest.mark.parametrize(
        "start_date,end_date,expected_start_datetime,expected_end_datetime",
        [
            (None, None, "..", ".."),
            ("2023-01-01", None, "2023-01-01T00:00:00Z", ".."),
            (None, "2023-12-31", "..", "2023-12-31T23:59:59Z"),
            (
                "2023-01-01",
                "2023-12-31",
                "2023-01-01T00:00:00Z",
                "2023-12-31T23:59:59Z",
            ),
        ],
    )
    @pytest.mark.parametrize("cql_query", [None, {"cql2": "query"}])
    @pytest.mark.parametrize("collections", [None, ["phr", "bjn"]])
    def test_should_search(
        self,
        bbox: glossary.BoundingBox | None,
        intersects: geojson.Polygon | None,
        start_date: str | None,
        end_date: str | None,
        expected_start_datetime: str,
        expected_end_datetime: str,
        cql_query: dict | None,
        collections: list[str] | None,
        requests_mock: req_mock.Mocker,
    ):
        search_params: dict[str, Any] = {}
        if bbox:
            search_params["bbox"] = bbox
        if intersects:
            search_params["intersects"] = intersects
        if start_date or end_date:
            search_params["datetime"] = f"{expected_start_datetime}/{expected_end_datetime}"
        if cql_query:
            search_params["query"] = cql_query
        if collections:
            search_params["collections"] = collections

        next_page_url = f"{self.search_url}/next"
        requests_mock.post(
            url=self.search_url,
            json={
                "type": "FeatureCollection",
                "features": [SCENE_FEATURE] * 3,
                "links": [{"rel": "next", "href": next_page_url}],
            },
            additional_matcher=helpers.match_request_body(search_params),
        )
        requests_mock.post(
            url=next_page_url,
            json={
                "type": "FeatureCollection",
                "features": [SCENE_FEATURE] * 2,
                "links": [],
            },
            additional_matcher=helpers.match_request_body(search_params),
        )
        assert list(self.provider.search(bbox, intersects, cql_query, collections, start_date, end_date)) == [SCENE] * 5


class TestProductGlossary:
    @pytest.mark.parametrize(
        "collection_type",
        [
            None,
            glossary.CollectionType.ARCHIVE,
            glossary.CollectionType.TASKING,
        ],
    )
    @pytest.mark.parametrize("sort_by", [None, glossary.CollectionSorting.name])
    def test_should_get_collections(
        self,
        requests_mock: req_mock.Mocker,
        collection_type: glossary.CollectionType,
        sort_by: utils.SortingField | None,
    ):
        collections = [
            {
                "name": COLLECTION.name,
                "description": COLLECTION.description,
                "title": COLLECTION.title,
                "type": type_value.value,
                "integrations": INTEGRATION_VALUES,
                "providers": [dataclasses.asdict(COLLECTION.providers[0])],
                "dataProducts": [
                    {
                        "name": DATA_PRODUCT.name,
                        "title": DATA_PRODUCT.title,
                        "description": DATA_PRODUCT.description,
                        "id": DATA_PRODUCT.id,
                        "eulaId": DATA_PRODUCT.eula_id,
                    }
                ],
                "metadata": {
                    "productType": COLLECTION_METADATA.product_type,
                    "resolutionClass": COLLECTION_METADATA.resolution_class,
                    "resolutionValue": dataclasses.asdict(RESOLUTION_VALUE),
                },
            }
            for type_value in list(glossary.CollectionType)
        ]
        sorting_param = f"sort={sort_by}&" if sort_by else ""
        for page in [0, 1]:
            requests_mock.get(
                f"{constants.API_HOST}/v2/collections?{sorting_param}page={page}",
                json={"content": collections, "totalPages": 2},
            )
        possible_types = [collection_type] if collection_type else list(glossary.CollectionType)
        assert (
            list(glossary.ProductGlossary.get_collections(collection_type=collection_type, sort_by=sort_by))
            == [dataclasses.replace(COLLECTION, type=possible_type) for possible_type in possible_types] * 2
        )
