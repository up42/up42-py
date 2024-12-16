import dataclasses
from typing import List, Optional

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import glossary, utils

DATA_PRODUCT = glossary.DataProduct(
    name="data-product-name",
    title="data-product-title",
    description="data-product",
    id="data-product-id",
    eula_id="eula-id",
)
RESOLUTION_VALUE = glossary.ResolutionValue(minimum=0.0, maximum=1.0, description="resolution value")
INTEGRATION_VALUES: List[glossary.IntegrationValue] = [
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
        sort_by: Optional[utils.SortingField],
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
