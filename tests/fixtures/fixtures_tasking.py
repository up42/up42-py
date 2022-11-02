from pathlib import Path
import json

import pytest

from .fixtures_globals import DATA_PRODUCT_ID

from ..context import (
    Tasking,
)


@pytest.fixture()
def tasking_mock(auth_mock, requests_mock):
    url_data_product_schema = f"{auth_mock._endpoint()}/orders/schema/{DATA_PRODUCT_ID}"
    with open(
        Path(__file__).resolve().parents[1]
        / "mock_data/data_product_schema_tasking.json"
    ) as json_file:
        json_data_product_schema = json.load(json_file)
        requests_mock.get(url=url_data_product_schema, json=json_data_product_schema)

    return Tasking(auth=auth_mock)
