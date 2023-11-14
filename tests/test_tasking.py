import json
import os
from pathlib import Path

import pytest
import requests

# pylint: disable=unused-import
from .fixtures import (
    DATA_PRODUCT_ID,
    QUOTATION_ID,
    WORKSPACE_ID,
    WRONG_FEASIBILITY_ID,
    WRONG_OPTION_ID,
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    tasking_choose_feasibility_mock,
    tasking_get_feasibility_mock,
    tasking_live,
    tasking_mock,
    username_test_live,
)

LIVE_TEST_WORKSPACE_ID = os.getenv("LIVE_TEST_WORKSPACE_ID")
LIVE_FEASIBILITY_ID = os.getenv("LIVE_FEASIBILITY_ID")
LIVE_OPTION_ID = os.getenv("LIVE_OPTION_ID")

with open(
    Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
) as json_file:
    mock_search_parameters = json.load(json_file)


def test_construct_order_parameters(tasking_mock):
    order_parameters = tasking_mock.construct_order_parameters(
        data_product_id=DATA_PRODUCT_ID,
        name="my_tasking_order",
        acquisition_start="2022-11-01",
        acquisition_end="2022-11-10",
        geometry=mock_search_parameters["intersects"],
    )
    assert isinstance(order_parameters, dict)
    assert list(order_parameters.keys()) == ["dataProduct", "params"]
    assert order_parameters["params"]["acquisitionMode"] is None


@pytest.mark.skip(reason="No live tests in the SDK.")
@pytest.mark.live
@pytest.mark.parametrize(
    "product_id",
    [
        ("613ad1f5-4148-4460-a316-1a97e46058f9"),
        ("83e21b35-e431-43a0-a1c4-22a6ad313911"),
        ("205fd9e1-4b00-4f0a-aabd-01e2f3f4dfba"),
        ("123eabab-0511-4f36-883a-80928716c3db"),
        ("07c33a51-94b9-4509-84df-e9c13ea92b84"),
        ("469f9b2f-1631-4c09-b66d-575abd41dc8f"),
        ("bd102407-1814-4f92-8b5a-7697b7a73f5a"),
        ("4f866cd3-d816-4c98-ace3-e6105623cf13"),
        ("28d4a077-6620-4ab5-9a03-c96bf622457e"),
        ("9d16c506-a6c0-4cf2-a020-8ecaf10b4160"),
        ("3a89d24e-515a-460f-a494-96be55da10a9"),
        ("47a693ba-4f8b-414d-8d5b-697373df4765"),
        ("9f790255-e8dc-4954-b5f9-3e7bea37cc69"),
        ("a6f64332-3148-4e05-a475-45a02176f210"),
    ],
)
def test_construct_order_parameters_live(tasking_live, product_id):
    order_parameters = tasking_live.construct_order_parameters(
        data_product_id=product_id,
        name="test_construct_order_params",
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
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility(
        decision=["NOT_DECIDED"]
    )
    assert len(feasibility_studies) == 1
    feasibility_studies = tasking_get_feasibility_mock.get_feasibility(
        decision=["some_wrong_string"]
    )
    assert len(feasibility_studies) == 26


@pytest.mark.skip(reason="No live tests in the SDK.")
@pytest.mark.live
def test_get_feasibility_live(tasking_live):
    feasibility_studies = tasking_live.get_feasibility()
    assert len(feasibility_studies) > 10
    feasibility_studies = tasking_live.get_feasibility(
        workspace_id=LIVE_TEST_WORKSPACE_ID
    )
    accepted_studies = (
        feasibility["workspaceId"] == LIVE_TEST_WORKSPACE_ID
        for feasibility in feasibility_studies
    )
    assert all(accepted_studies)

    feasibility_studies = tasking_live.get_feasibility(decision=["ACCEPTED"])
    accepted_studies = (
        feasibility["decision"] == "ACCEPTED" for feasibility in feasibility_studies
    )
    assert len(list(accepted_studies)) > 10
    assert all(accepted_studies)

    feasibility_studies = tasking_live.get_feasibility(
        decision=["ACCEPTED", "NOT_DECIDED"]
    )
    accepted_studies = (
        feasibility["decision"] in ["ACCEPTED", "NOT_DECIDED"]
        for feasibility in feasibility_studies
    )
    assert len(list(accepted_studies)) > 10
    assert all(accepted_studies)
    feasibility_studies = tasking_live.get_feasibility(
        feasibility_id=WRONG_FEASIBILITY_ID
    )
    assert len(feasibility_studies) == 0


def test_choose_feasibility(tasking_choose_feasibility_mock):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_choose_feasibility_mock.choose_feasibility(
            WRONG_FEASIBILITY_ID, WRONG_OPTION_ID
        )
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 404

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_choose_feasibility_mock.choose_feasibility(
            LIVE_FEASIBILITY_ID, LIVE_OPTION_ID
        )
    response = json.loads(str(e.value))
    assert isinstance(e.value, requests.exceptions.RequestException)
    assert response["status"] == 405


@pytest.mark.skip(reason="No live tests in the SDK.")
@pytest.mark.live
def test_choose_feasibility_live(tasking_live):
    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_live.choose_feasibility(WRONG_FEASIBILITY_ID, WRONG_OPTION_ID)
        assert isinstance(e.value, requests.exceptions.RequestException)
        assert "404" in str(e.value)

    with pytest.raises(requests.exceptions.RequestException) as e:
        tasking_live.choose_feasibility(LIVE_FEASIBILITY_ID, LIVE_OPTION_ID)
        assert isinstance(e.value, requests.exceptions.RequestException)
        assert (
            str(e.value)
            == "{'status': 405, 'title': 'Resource (FeasibilityStudy) is write-protected.', 'detail': None}"
        )
