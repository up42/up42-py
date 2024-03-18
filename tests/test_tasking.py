import json
import pathlib

import pytest
import requests

from .fixtures import fixtures_globals as constants

with open(
    pathlib.Path(__file__).resolve().parent / "mock_data/search_params_simple.json", encoding="utf-8"
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_construct_order_parameters(tasking_mock):
    order_parameters = tasking_mock.construct_order_parameters(
        data_product_id=constants.DATA_PRODUCT_ID,
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
    get_workspace_quotations = tasking_mock.get_quotations(workspace_id=constants.WORKSPACE_ID)
    assert all(quotation["workspaceId"] == constants.WORKSPACE_ID for quotation in get_workspace_quotations)
    get_accepted_quotations = tasking_mock.get_quotations(decision=["ACCEPTED"])
    assert all(quotation["decision"] == "ACCEPTED" for quotation in get_accepted_quotations)
    get_decided_quotations = tasking_mock.get_quotations(decision=["ACCEPTED", "REJECTED"])
    assert all(quotation["decision"] in ["ACCEPTED", "REJECTED"] for quotation in get_decided_quotations)


def test_decide_quotation(tasking_mock):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_mock.decide_quotation(constants.QUOTATION_ID + "-01", "ACCEPTED")
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 404

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_mock.decide_quotation(constants.QUOTATION_ID + "-02", "ACCEPTED")
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 405


def test_get_feasibility(tasking_get_feasibility_mock):
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility()
    assert len(feasibility_studies) == 26
    assert list(feasibility_studies[0].keys()) == [
        "id",
        "createdAt",
        "updatedAt",
        "accountId",
        "workspaceId",
        "orderId",
        "type",
        "options",
        "decision",
        "decisionById",
        "decisionByType",
        "decisionAt",
        "decisionOption",
    ]
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility(decision=["NOT_DECIDED"])
    assert len(feasibility_studies) == 1
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility(decision=["some_wrong_string"])
    assert len(feasibility_studies) == 26


def test_choose_feasibility(tasking_choose_feasibility_mock):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_choose_feasibility_mock.choose_feasibility(constants.WRONG_FEASIBILITY_ID, constants.WRONG_OPTION_ID)
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 404

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_choose_feasibility_mock.choose_feasibility(constants.TEST_FEASIBILITY_ID, constants.TEST_OPTION_ID)
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 405
