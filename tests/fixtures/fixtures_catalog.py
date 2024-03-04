import copy
import json
from pathlib import Path

import pytest

from up42.catalog import Catalog

from .fixtures_globals import API_HOST, DATA_PRODUCT_ID


@pytest.fixture()
def catalog_mock(auth_mock, requests_mock):
    url_collections = f"{API_HOST}/collections"
    collections_response = {
        "data": [{"name": "phr", "hostName": "oneatlas", "type": "ARCHIVE"}]
    }
    requests_mock.get(
        url=url_collections,
        json=collections_response,
    )

    url_data_products = f"{API_HOST}/data-products"
    with open(
        Path(__file__).resolve().parents[1] / "mock_data/data_products.json"
    ) as json_file:
        json_data_products = json.load(json_file)
        requests_mock.get(
            url=url_data_products, json={"data": json_data_products}
        )

    url_search = f"{API_HOST}/catalog/hosts/oneatlas/stac/search"
    with open(
        Path(__file__).resolve().parents[1] / "mock_data/search_response.json"
    ) as json_file:
        json_search_response = json.load(json_file)
    requests_mock.post(
        url=url_search,
        json=json_search_response,
    )

    url_data_product_schema = f"{API_HOST}/orders/schema/{DATA_PRODUCT_ID}"
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/data_product_spot_schema.json"
    ) as json_file:
        json_data_product_schema = json.load(json_file)
        requests_mock.get(
            url=url_data_product_schema, json=json_data_product_schema
        )

    return Catalog(auth=auth_mock)


@pytest.fixture()
def catalog_live(auth_live):
    return Catalog(auth=auth_live)


@pytest.fixture()
def catalog_pagination_mock(auth_mock, requests_mock):
    url_collections = f"{API_HOST}/collections"
    collections_response = {
        "data": [{"name": "phr", "hostName": "oneatlas", "type": "ARCHIVE"}]
    }
    requests_mock.get(
        url=url_collections,
        json=collections_response,
    )

    url_data_products = f"{API_HOST}/data-products"
    with open(
        Path(__file__).resolve().parents[1] / "mock_data/data_products.json"
    ) as json_file:
        json_data_products = json.load(json_file)
        requests_mock.get(
            url=url_data_products, json={"data": json_data_products}
        )

    with open(
        Path(__file__).resolve().parents[1] / "mock_data/search_response.json"
    ) as json_file:
        search_response_json = json.load(json_file)
    search_response_json["features"] = search_response_json["features"] * 500

    pagination_response_json = copy.deepcopy(search_response_json)
    pagination_response_json["features"] = pagination_response_json[
        "features"
    ][:50]
    del pagination_response_json["links"][
        1
    ]  # indicator of pagination exhaustion (after first page)

    url_search = f"{API_HOST}/catalog/hosts/oneatlas/stac/search"
    requests_mock.post(
        url_search,
        [{"json": search_response_json}, {"json": pagination_response_json}],
    )

    return Catalog(auth=auth_mock)


@pytest.fixture()
def catalog_usagetype_mock(auth_mock, requests_mock):
    url_collections = f"{API_HOST}/collections"
    collections_response = {
        "data": [{"name": "phr", "hostName": "oneatlas", "type": "ARCHIVE"}]
    }
    requests_mock.get(
        url=url_collections,
        json=collections_response,
    )

    url_data_products = f"{API_HOST}/data-products"
    with open(
        Path(__file__).resolve().parents[1] / "mock_data/data_products.json"
    ) as json_file:
        json_data_products = json.load(json_file)
        requests_mock.get(
            url=url_data_products, json={"data": json_data_products}
        )

    with open(
        Path(__file__).resolve().parents[1] / "mock_data/search_response.json"
    ) as json_file:
        search_response_json = json.load(
            json_file
        )  # original response is usagetype data

    response_analytics = copy.deepcopy(search_response_json)
    response_analytics["features"][0]["properties"]["up42:usageType"] = [
        "ANALYTICS"
    ]
    response_data_and_analytics = copy.deepcopy(search_response_json)
    response_data_and_analytics["features"][0]["properties"][
        "up42:usageType"
    ] = [
        "DATA",
        "ANALYTICS",
    ]

    url_search = f"{API_HOST}/catalog/hosts/oneatlas/stac/search"
    requests_mock.post(
        url_search,
        [
            {"json": search_response_json},
            {"json": response_analytics},
            {"json": response_data_and_analytics},
        ],
    )

    return Catalog(auth=auth_mock)
