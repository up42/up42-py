import json
import pathlib

import pytest

from up42 import catalog

from . import fixtures_globals as constants


@pytest.fixture
def catalog_mock(auth_mock, requests_mock):
    url_data_product_schema = f"{constants.API_HOST}/orders/schema/{constants.DATA_PRODUCT_ID}"
    with open(
        pathlib.Path(__file__).resolve().parents[1] / "mock_data/data_product_spot_schema.json",
        encoding="utf-8",
    ) as json_file:
        json_data_product_schema = json.load(json_file)
        requests_mock.get(url=url_data_product_schema, json=json_data_product_schema)

    return catalog.Catalog(auth=auth_mock, workspace_id=constants.WORKSPACE_ID)
