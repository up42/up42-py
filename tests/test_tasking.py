from pathlib import Path
import json

# pylint: disable=unused-import
from .fixtures import (
    tasking_mock,
)

with open(
    Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_construct_order_parameters(tasking_mock):
    order_parameters = tasking_mock.construct_order_parameters(
        data_product_id="data_product_id_123",
        image_id="123",
        aoi=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
