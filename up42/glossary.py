import dataclasses
import enum
from typing import Any, Iterator, Literal, Optional

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
    name: str
    title: str
    description: str
    id: Optional[str]
    eula_id: Optional[str]


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
