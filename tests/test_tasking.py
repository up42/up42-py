from pathlib import Path
import json
import requests
import pytest

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    tasking_mock,
    tasking_live,
    WORKSPACE_ID,
    QUOTATION_ID,
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


def test_get_quotations(tasking_mock):
    get_quotations = tasking_mock.get_quotations()
    assert len(get_quotations) == 23
    get_quotations = tasking_mock.get_quotations(workspace_id=WORKSPACE_ID)
    quotations_accepted = (
        quotation["workspaceId"] == WORKSPACE_ID for quotation in get_quotations
    )
    assert all(quotations_accepted)
    get_quotations = tasking_mock.get_quotations(decision=["ACCEPTED"])
    quotations_accepted = (
        quotation["decision"] == "ACCEPTED" for quotation in get_quotations
    )
    assert all(quotations_accepted)
    get_quotations = tasking_mock.get_quotations(decision=["ACCEPTED", "REJECTED"])
    quotations_accepted = (
        quotation["decision"] in ["ACCEPTED", "REJECTED"]
        for quotation in get_quotations
    )
    assert all(quotations_accepted)


def test_decide_quotation(tasking_mock):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_mock.decide_quotation(QUOTATION_ID + "-01", "ACCEPTED")
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 404

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_mock.decide_quotation(QUOTATION_ID + "-02", "ACCEPTED")
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 405


@pytest.mark.skip(reason="No live tests in the SDK.")
@pytest.mark.live
def test_get_quotations_live(tasking_live):
    get_quotations = tasking_live.get_quotations()
    assert len(get_quotations) > 10
    workspace_id_filter = "80357ed6-9fa2-403c-9af0-65e4955d4816"

    get_quotations = tasking_live.get_quotations(workspace_id=workspace_id_filter)
    quotations_accepted = (
        quotation["workspaceId"] == workspace_id_filter for quotation in get_quotations
    )
    assert all(quotations_accepted)

    get_quotations = tasking_live.get_quotations(decision=["ACCEPTED"])
    quotations_accepted = (
        quotation["decision"] == "ACCEPTED" for quotation in get_quotations
    )
    assert all(quotations_accepted)

    get_quotations = tasking_live.get_quotations(decision=["ACCEPTED", "REJECTED"])
    quotations_accepted = (
        quotation["decision"] in ["ACCEPTED", "REJECTED"]
        for quotation in get_quotations
    )
    assert all(quotations_accepted)


@pytest.mark.skip(reason="No live tests in the SDK.")
@pytest.mark.live
def test_decide_quotations_live(tasking_live):
    wrong_quotation_id = "296ef1b0-d890-430d-8d14-e9b579ab08ba"
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_live.decide_quotation(wrong_quotation_id, "ACCEPTED")
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert "404" in str(e.value)

    accepted_quotation_id = "296ef1b0-d890-430d-8d14-e9b579ab08bd"
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_live.decide_quotation(accepted_quotation_id, "ACCEPTED")
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert "405" in str(e.value)
