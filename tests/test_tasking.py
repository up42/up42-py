import dataclasses
import urllib.parse
import uuid
from typing import Any, List, Optional

import pytest
import requests_mock as req_mock

from tests import constants, helpers
from up42 import tasking, utils

ACQ_START = "2014-01-01T00:00:00"
ACQ_END = "2022-12-31T23:59:59"
ORDER_NAME = "order-name"
POINT = {"type": "Point", "coordinates": (1.0, 2.0)}
POLYGON = {
    "type": "Polygon",
    "coordinates": (
        (
            (1.0, 1.0),
            (2.0, 1.0),
            (2.0, 2.0),
            (1.0, 2.0),
            (1.0, 1.0),
        ),
    ),
}

QUOTATION_ID = "805b1f27-1025-43d2-90d0-0bd3416238fb"
FEASIBILITY_ID = "6f93f754-5594-42da-b6af-9064225b89e9"
ACCOUNT_ID = str(uuid.uuid4())


class TestQuotation:
    metadata = {
        "id": QUOTATION_ID,
        "createdAt": "created-at",
        "updatedAt": "updated-at",
        "decisionAt": "decided-at",
        "accountId": ACCOUNT_ID,
        "workspaceId": constants.WORKSPACE_ID,
        "orderId": constants.ORDER_ID,
        "creditsPrice": 10,
        "decision": "ACCEPTED",
    }
    quotation = tasking.Quotation(
        id=QUOTATION_ID,
        created_at="created-at",
        updated_at="updated-at",
        decided_at="decided-at",
        account_id=ACCOUNT_ID,
        workspace_id=constants.WORKSPACE_ID,
        order_id=constants.ORDER_ID,
        credits_price=10,
        decision="ACCEPTED",
    )

    def test_should_accept(self):
        undecided = dataclasses.replace(self.quotation, decision="NOT_DECIDED")
        undecided.accept()
        assert undecided == self.quotation

    def test_should_reject(self):
        undecided = dataclasses.replace(self.quotation, decision="NOT_DECIDED")
        undecided.reject()
        assert undecided == dataclasses.replace(self.quotation, decision="REJECTED")

    @pytest.mark.parametrize("decision", ["ACCEPTED", "REJECTED"])
    def test_should_save(self, requests_mock: req_mock.Mocker, decision: tasking.QuotationDecision):
        undecided = dataclasses.replace(self.quotation, decision="NOT_DECIDED", decided_at=None)
        patch = {"decision": decision}
        url = f"{constants.API_HOST}/v2/tasking/quotation/{QUOTATION_ID}"
        requests_mock.patch(
            url=url,
            json=self.metadata | patch,
            additional_matcher=helpers.match_request_body(patch),
        )
        undecided.decision = decision
        undecided.save()
        assert undecided == dataclasses.replace(self.quotation, decision=decision)

    @pytest.mark.parametrize("quotation_id", [None, QUOTATION_ID])
    @pytest.mark.parametrize("workspace_id", [None, constants.WORKSPACE_ID])
    @pytest.mark.parametrize("order_id", [None, constants.ORDER_ID])
    @pytest.mark.parametrize("decision", [None, ["ACCEPTED", "REJECTED", "NOT_DECIDED"], ["ACCEPTED"]], ids=str)
    @pytest.mark.parametrize(
        "sort_by",
        [
            None,
            tasking.QuotationSorting.created_at.asc,
            tasking.QuotationSorting.credits_price.asc,
            tasking.QuotationSorting.decided_at.asc,
            tasking.QuotationSorting.updated_at.asc,
        ],
        ids=str,
    )
    def test_should_get_all(
        self,
        requests_mock: req_mock.Mocker,
        quotation_id: str | None,
        workspace_id: str | None,
        order_id: str | None,
        decision: list[tasking.QuotationStatus] | None,
        sort_by: utils.SortingField | None,
    ):
        query_params: dict[str, Any] = {}
        if quotation_id:
            query_params["id"] = quotation_id
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if order_id:
            query_params["orderId"] = order_id
        if decision:
            query_params["decision"] = decision
        if sort_by:
            query_params["sort"] = str(sort_by)

        base_url = f"{constants.API_HOST}/v2/tasking/quotation"
        expected = [self.metadata] * 4
        for page in [0, 1]:
            query_params["page"] = page
            query = urllib.parse.urlencode(query_params, doseq=True, safe="")
            url = base_url + (query and f"?{query}")
            offset = page * 2
            response = {
                "content": expected[offset : offset + 2],  # noqa: E203
                "totalPages": 2,
            }
            requests_mock.get(url=url, json=response)

        quotations = tasking.Quotation.all(
            quotation_id=quotation_id,
            workspace_id=workspace_id,
            order_id=order_id,
            decision=decision,
            sort_by=sort_by,
        )
        assert list(quotations) == [self.quotation] * 4


class TestFeasibilityStudy:
    FEASIBILITY_ID: str = FEASIBILITY_ID
    ACCOUNT_ID: str = ACCOUNT_ID
    WORKSPACE_ID: str = "workspace-id"
    ORDER_ID: str = "test-order-id"
    OPTION_ID: str = "option-123"

    metadata: dict = {
        "id": FEASIBILITY_ID,
        "createdAt": "created-at",
        "updatedAt": "updated-at",
        "accountId": ACCOUNT_ID,
        "workspaceId": WORKSPACE_ID,
        "orderId": ORDER_ID,
        "decision": "NOT_DECIDED",
        "options": [{"id": OPTION_ID}],
        "decisionAt": "decided-at",
    }
    feasibility_study = tasking.FeasibilityStudy(
        id=FEASIBILITY_ID,
        created_at="created-at",
        updated_at="updated-at",
        account_id=ACCOUNT_ID,
        workspace_id=WORKSPACE_ID,
        order_id=ORDER_ID,
        decision="NOT_DECIDED",
        options=[{"id": OPTION_ID}],
        decided_at="decided-at",
        decision_option=None,
    )

    @pytest.mark.parametrize("feasibility_study_id", [None, FEASIBILITY_ID])
    @pytest.mark.parametrize("workspace_id", [None, WORKSPACE_ID])
    @pytest.mark.parametrize("order_id", [None, ORDER_ID])
    @pytest.mark.parametrize("decision", [None, ["NOT_DECIDED", "ACCEPTED"], ["ACCEPTED"]])
    @pytest.mark.parametrize(
        "sort_by",
        [
            None,
            tasking.FeasibilityStudySorting.created_at.asc,
            tasking.FeasibilityStudySorting.updated_at.asc,
            tasking.FeasibilityStudySorting.decided_at.asc,
        ],
        ids=str,
    )
    def test_should_get_all(
        self,
        requests_mock: req_mock.Mocker,
        feasibility_study_id: str | None,
        workspace_id: str | None,
        order_id: str | None,
        decision: list[tasking.FeasibilityStatus] | None,
        sort_by: utils.SortingField | None,
    ):
        query_params: dict[str, Any] = {}
        if feasibility_study_id:
            query_params["id"] = feasibility_study_id
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if order_id:
            query_params["orderId"] = order_id
        if decision:
            query_params["decision"] = decision
        if sort_by:
            query_params["sort"] = str(sort_by)
        base_url = f"{constants.API_HOST}/v2/tasking/feasibility-studies"
        expected = [self.metadata] * 4
        for page in [0, 1]:
            query_params["page"] = page
            query = urllib.parse.urlencode(query_params, doseq=True, safe="")
            url = base_url + (query and f"?{query}")
            offset = page * 2
            response = {
                "content": expected[offset : offset + 2],  # noqa: E203
                "totalPages": 2,
            }
            requests_mock.get(url=url, json=response)
        feasibility_studies = tasking.FeasibilityStudy.all(
            feasibility_study_id=feasibility_study_id,
            workspace_id=workspace_id,
            order_id=order_id,
            decision=decision,
            sort_by=sort_by,
        )
        assert list(feasibility_studies) == [self.feasibility_study] * 4

    def test_should_accept(self):
        feasibility_study = dataclasses.replace(self.feasibility_study, decision_option=None)
        feasibility_study.accept(self.OPTION_ID)
        assert feasibility_study.decision_option.id == self.OPTION_ID  # type: ignore[union-attr]

    def test_should_save(self, requests_mock: req_mock.Mocker):
        feasibility_study = dataclasses.replace(self.feasibility_study, decision_option=None)
        feasibility_study.accept(self.OPTION_ID)
        patch = {"acceptedOptionId": self.OPTION_ID}
        url = f"{constants.API_HOST}/v2/tasking/feasibility-studies/{self.FEASIBILITY_ID}"
        expected_description = "description"
        expected_json = self.metadata | {"decisionOption": {"id": self.OPTION_ID, "description": expected_description}}
        requests_mock.patch(
            url=url,
            json=expected_json,
            additional_matcher=helpers.match_request_body(patch),
        )
        feasibility_study.save()
        assert feasibility_study.decision_option.id == self.OPTION_ID  # type: ignore[union-attr]
        assert feasibility_study.decision_option.description == expected_description  # type: ignore[union-attr]

    def test_should_raise_if_no_decision_option_on_save(self):
        feasibility_study = dataclasses.replace(self.feasibility_study, decision_option=None)
        with pytest.raises(
            feasibility_study.NoDecisionOptionChosen, match="No decision option chosen for this feasibility study."
        ):
            feasibility_study.save()
