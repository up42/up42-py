from pathlib import Path
import pytest
import json

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    tasking_mock,
    tasking_live,
)

with open(
    Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_construct_order_parameters(tasking_mock):
    order_parameters = tasking_mock.construct_order_parameters(
        data_product_id="data_product_id_123",
        name="my_tasking_order",
        acquisition_start="2022-11-01",
        acquisition_end="2022-11-10",
        geometry=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


@pytest.mark.live
def test_get_quotations(tasking_live):
    get_quotations = tasking_live.get_quotations()
    assert len(get_quotations) > 10
    workspace_id_filter = "80357ed6-9fa2-403c-9af0-65e4955d4816"
    get_quotations = tasking_live.get_quotations(
        workspace_id=workspace_id_filter
    )
    assert all([quotation["workspaceId"] == workspace_id_filter for quotation in get_quotations])
    get_quotations = tasking_live.get_quotations(decision="ACCEPTED")
    assert all([quotation["decision"] == "ACCEPTED" for quotation in get_quotations])