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


class InvalidHost(ValueError):
    pass


@dataclasses.dataclass
class Provider:
    session = base.Session()
    name: str
    title: str
    description: str
    roles: list[Literal["PRODUCER", "HOST"]]

    @property
    def is_host(self):
        return "HOST" in self.roles

    def search(
        self,
        bbox: Optional[tuple[float, float, float, float]] = None,
        intersects: Optional[geojson.Polygon] = None,
        datetime: Optional[str] = None,
        query: Optional[dict] = None,
        collections: Optional[list[str]] = None,
    ) -> Iterator[Scene]:
        if not self.is_host:
            raise InvalidHost("Provider does not host collections")
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

        def get_pages():
            url = host.endpoint(f"/catalog/hosts/{self.name}/stac/search")
            while url:
                page: dict = self.session.post(url, json=payload).json()
                yield page["features"]
                url = next(
                    (link["href"] for link in page["links"] if link["rel"] == "next"),
                    None,
                )

        for page in get_pages():
            for feature in page:
                yield self._as_scene(feature)

    def _as_scene(self, feature: geojson.Feature) -> Scene:
        properties = feature["properties"]
        return Scene(
            bbox=feature.get("bbox"),
            geometry=feature["geometry"],
            id=properties["id"],
            constellation=properties["constellation"],
            collection=properties["collection"],
            producer=properties["producer"],
            datetime=properties.get("datetime"),
            start_datetime=properties.get("start_datetime"),
            end_datetime=properties.get("end_datetime"),
            cloud_coverage=properties.get("cloudCoverage"),
            resolution=properties.get("resolution"),
            delivery_time=properties.get("deliveryTime"),
        )


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
