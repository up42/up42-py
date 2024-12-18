import dataclasses
import enum
from typing import Any, Iterator, Literal, Optional

import geojson  # type: ignore

from up42 import base, host, utils


class CollectionType(enum.Enum):
    ARCHIVE = "ARCHIVE"
    TASKING = "TASKING"


IntegrationValue = Literal[
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


@dataclasses.dataclass
class ResolutionValue:
    minimum: float
    description: Optional[str] = None
    maximum: Optional[float] = None


@dataclasses.dataclass
class CollectionMetadata:
    product_type: Optional[Literal["OPTICAL", "SAR", "ELEVATION"]]
    resolution_class: Optional[Literal["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]]
    resolution_value: Optional[ResolutionValue]


@dataclasses.dataclass
class Provider:
    name: str
    title: str
    description: str
    roles: list[Literal["PRODUCER", "HOST"]]


@dataclasses.dataclass
class DataProduct:
    session = base.Session()
    name: str
    title: str
    description: str
    id: Optional[str]
    eula_id: Optional[str]

    @property
    def schema(self) -> Optional[dict]:
        if self.id:
            url = host.endpoint(f"/orders/schema/{self.id}")
            return self.session.get(url).json()
        else:
            return None


@dataclasses.dataclass
class Collection:
    name: str
    title: str
    description: str
    type: CollectionType
    integrations: list[IntegrationValue]
    providers: list[Provider]
    data_products: list[DataProduct]
    metadata: Optional[CollectionMetadata]


@dataclasses.dataclass
class Quicklook:
    session = base.Session()
    scene_id: str
    host_name: str

    def download(self):
        pass


@dataclasses.dataclass
class Scene:
    bbox: Optional[tuple[float, float, float, float]]
    geometry: geojson.Polygon
    id: str
    datetime: Optional[str]
    start_datetime: Optional[str]
    end_datetime: Optional[str]
    constellation: str
    collection: str
    cloud_coverage: Optional[float]
    resolution: Optional[float]
    delivery_time: Optional[Literal["MINUTES", "HOURS", "DAYS"]]
    producer: str
    quicklook: Quicklook


@dataclasses.dataclass
class Host:
    session = base.Session()
    name: str
    title: str
    description: str
    collections: list[Collection]

    def search(
        self,
        bbox: Optional[tuple[float, float, float, float]] = None,
        intersects: Optional[geojson.Polygon] = None,
        datetime: Optional[str] = None,
        query: Optional[dict] = None,
        collections: Optional[list[str]] = None,
    ) -> list[Scene]:
        payload = {
            key: value
            for key, value in {
                "bbox": bbox,
                "intersects": intersects,
                "datetime": datetime,
                "query": query,
                "collections": collections,
            }.items()
            if value
        }
        url = host.endpoint(f"/catalog/hosts/{self.name}/stac/search")
        features = []

        while url:
            page: dict = self.session.post(url, json=payload).json()
            features += page["features"]
            url = next((link["href"] for link in page["links"] if link["rel"] == "next"), None)
        return [
            Scene(
                bbox=feature.get("bbox"),
                geometry=feature["geometry"],
                id=feature["properties"]["id"],
                datetime=feature["properties"].get("datetime"),
                start_datetime=feature["properties"].get("start_datetime"),
                end_datetime=feature["properties"].get("end_datetime"),
                constellation=feature["properties"]["constellation"],
                collection=feature["properties"]["collection"],
                cloud_coverage=feature["properties"].get("cloudCoverage"),
                resolution=feature["properties"].get("resolution"),
                delivery_time=feature["properties"].get("deliveryTime"),
                producer=feature["properties"]["producer"],
                quicklook=Quicklook(scene_id=feature["properties"]["id"], host_name=self.name),
            )
            for feature in features
        ]


class CollectionSorting:
    name = utils.SortingField("name")
    title = utils.SortingField("title")
    description = utils.SortingField("description")
    type = utils.SortingField("type")


class ProductGlossary:
    session = base.Session()

    @classmethod
    def get_collections(
        cls,
        collection_type: Optional[CollectionType] = None,
        sort_by: Optional[utils.SortingField] = None,
    ) -> Iterator[Collection]:
        query_params: dict[str, Any] = {"sort": sort_by} if sort_by else {}

        def get_pages():
            current_page = 0
            while True:
                query_params["page"] = current_page
                page = cls.session.get(host.endpoint("/v2/collections"), params=query_params).json()
                total_pages = page["totalPages"]
                yield page["content"]
                current_page += 1
                if current_page == total_pages:
                    break

        for page_content in get_pages():
            for collection in page_content:
                if collection_type is None or collection["type"] == collection_type.value:
                    metadata = collection.get("metadata")
                    yield Collection(
                        name=collection["name"],
                        title=collection["title"],
                        description=collection["description"],
                        type=CollectionType(collection["type"]),
                        integrations=collection["integrations"],
                        providers=[Provider(**provider) for provider in collection["providers"]],
                        data_products=[
                            DataProduct(
                                name=data_product["name"],
                                title=data_product["title"],
                                description=data_product["description"],
                                id=data_product.get("id"),
                                eula_id=data_product.get("eulaId"),
                            )
                            for data_product in collection["dataProducts"]
                        ],
                        metadata=metadata
                        and CollectionMetadata(
                            product_type=metadata.get("productType"),
                            resolution_class=metadata.get("resolutionClass"),
                            resolution_value=metadata.get("resolutionValue")
                            and ResolutionValue(**metadata.get("resolutionValue")),
                        ),
                    )

    @classmethod
    def get_hosts(cls, collection_type: Optional[CollectionType] = None):
        collections = list(cls.get_collections(collection_type=collection_type))
        hosting_providers = [
            provider for collection in collections for provider in collection.providers if "HOST" in provider.roles
        ]
        hosts = [
            Host(
                name=provider.name,
                title=provider.title,
                description=provider.description,
                collections=[],
            )
            for provider in hosting_providers
        ]
        for host_, provider in zip(hosts, hosting_providers):
            for collection in collections:
                if provider in collection.providers:
                    host_.collections.append(collection)

        return hosts
