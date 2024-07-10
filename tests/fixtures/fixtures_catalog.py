import copy
import json
import pathlib

import pytest

from up42 import catalog
from . import fixtures_globals as constants


@pytest.fixture
def catalog_mock(auth_mock, requests_mock):
    url_data_products = f"{constants.API_HOST}/data-products"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/data_products.json",
        encoding="utf-8",
    ) as json_file:
        json_data_products = json.load(json_file)
        requests_mock.get(url=url_data_products, json={"data": json_data_products})

    url_search = f"{constants.API_HOST}/catalog/hosts/oneatlas/stac/search"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/search_response.json",
        encoding="utf-8",
    ) as json_file:
        json_search_response = json.load(json_file)
    requests_mock.post(
        url=url_search,
        json=json_search_response,
    )

    url_data_product_schema = (
        f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
    )
    with open(
        pathlib.Path(__file__).resolve().parents[1]
        / "mock_data/data_product_spot_schema.json",
        encoding="utf-8",
    ) as json_file:
        json_data_product_schema = json.load(json_file)
        requests_mock.get(url=url_data_product_schema, json=json_data_product_schema)

    return catalog.Catalog(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)


@pytest.fixture
def catalog_pagination_mock(auth_mock, requests_mock):
    url_data_products = f"{constants.API_HOST}/data-products"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/data_products.json",
        encoding="utf-8",
    ) as json_file:
        json_data_products = json.load(json_file)
        requests_mock.get(url=url_data_products, json={"data": json_data_products})

    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/search_response.json",
        encoding="utf-8",
    ) as json_file:
        search_response_json = json.load(json_file)
    search_response_json["features"] = search_response_json["features"] * 500

    pagination_response_json = copy.deepcopy(search_response_json)
    pagination_response_json["features"] = pagination_response_json["features"][:50]
    del pagination_response_json["links"][
        1
    ]  # indicator of pagination exhaustion (after first page)

    url_search = f"{constants.API_HOST}/catalog/hosts/oneatlas/stac/search"
    requests_mock.post(
        url_search,
        [{"json": search_response_json}, {"json": pagination_response_json}],
    )

    return catalog.Catalog(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)


@pytest.fixture
def catalog_usagetype_mock(auth_mock, requests_mock):
    url_data_products = f"{constants.API_HOST}/data-products"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/data_products.json",
        encoding="utf-8",
    ) as json_file:
        json_data_products = json.load(json_file)
        requests_mock.get(url=url_data_products, json={"data": json_data_products})

    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/search_response.json",
        encoding="utf-8",
    ) as json_file:
        search_response_json = json.load(
            json_file
        )  # original response is usagetype data

    response_analytics = copy.deepcopy(search_response_json)
    response_analytics["features"][0]["properties"]["up42:usageType"] = ["ANALYTICS"]
    response_data_and_analytics = copy.deepcopy(search_response_json)
    response_data_and_analytics["features"][0]["properties"]["up42:usageType"] = [
        "DATA",
        "ANALYTICS",
    ]

    url_search = f"{constants.API_HOST}/catalog/hosts/oneatlas/stac/search"
    requests_mock.post(
        url_search,
        [
            {"json": search_response_json},
            {"json": response_analytics},
            {"json": response_data_and_analytics},
        ],
    )

    return catalog.Catalog(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
