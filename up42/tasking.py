"""
Tasking functionality
"""

import dataclasses
from collections.abc import Iterator
from typing import Literal, TypeAlias

from up42 import base, host, utils

logger = utils.get_logger(__name__)

QuotationDecision: TypeAlias = Literal[
    "ACCEPTED",
    "REJECTED",
]
QuotationStatus: TypeAlias = Literal["NOT_DECIDED"] | QuotationDecision
FeasibilityStatus: TypeAlias = Literal["NOT_DECIDED", "ACCEPTED"]


class QuotationSorting:
    created_at = utils.SortingField(name="createdAt")
    credits_price = utils.SortingField(name="creditsPrice")
    decided_at = utils.SortingField(name="decisionAt")
    updated_at = utils.SortingField(name="updatedAt")


@dataclasses.dataclass
class Quotation:
    session = base.Session()
    id: str
    created_at: str
    updated_at: str
    decided_at: str | None
    account_id: str
    workspace_id: str
    order_id: str
    credits_price: int
    decision: QuotationStatus

    def accept(self):
        self.decision = "ACCEPTED"

    def reject(self):
        self.decision = "REJECTED"

    def save(self):
        url = host.endpoint(f"/v2/tasking/quotation/{self.id}")
        metadata = self.session.patch(url, json={"decision": self.decision}).json()
        quotation = self._from_metadata(metadata)
        for field in dataclasses.fields(quotation):
            setattr(self, field.name, getattr(quotation, field.name))

    @staticmethod
    def _from_metadata(metadata: dict) -> "Quotation":
        return Quotation(
            id=metadata["id"],
            created_at=metadata["createdAt"],
            updated_at=metadata["updatedAt"],
            decided_at=metadata["decisionAt"],
            account_id=metadata["accountId"],
            workspace_id=metadata["workspaceId"],
            order_id=metadata["orderId"],
            credits_price=metadata["creditsPrice"],
            decision=metadata["decision"],
        )

    @classmethod
    def all(
        cls,
        quotation_id: str | None = None,
        workspace_id: str | None = None,
        order_id: str | None = None,
        decision: list[QuotationStatus] | None = None,
        sort_by: utils.SortingField | None = None,
    ) -> Iterator["Quotation"]:
        params = {
            "workspaceId": workspace_id,
            "id": quotation_id,
            "orderId": order_id,
            "decision": decision,
            "sort": sort_by,
        }
        return map(
            cls._from_metadata,
            utils.paged_query(params, "/v2/tasking/quotation", cls.session),
        )


class FeasibilityStudySorting:
    created_at = utils.SortingField(name="createdAt")
    updated_at = utils.SortingField(name="updatedAt")
    decided_at = utils.SortingField(name="decisionAt")


@dataclasses.dataclass
class FeasibilityStudyDecisionOption:
    id: str
    description: str | None = None


@dataclasses.dataclass
class FeasibilityStudy:
    session = base.Session()
    id: str
    created_at: str
    updated_at: str
    account_id: str
    workspace_id: str
    order_id: str
    decision: FeasibilityStatus
    options: list[dict]
    decided_at: str | None = None
    decision_option: FeasibilityStudyDecisionOption | None = None

    class NoDecisionOptionChosen(Exception):
        """Raised when trying to save a FeasibilityStudy without a chosen decision option."""

    @classmethod
    def all(
        cls,
        feasibility_study_id: str | None = None,
        workspace_id: str | None = None,
        order_id: str | None = None,
        decision: list[FeasibilityStatus] | None = None,
        sort_by: utils.SortingField | None = None,
    ) -> Iterator["FeasibilityStudy"]:
        params = {
            "id": feasibility_study_id,
            "workspaceId": workspace_id,
            "orderId": order_id,
            "decision": decision,
            "sort": sort_by,
        }
        return map(
            cls._from_metadata,
            utils.paged_query(params, "/v2/tasking/feasibility-studies", cls.session),
        )

    @staticmethod
    def _from_metadata(metadata: dict) -> "FeasibilityStudy":
        decision_option = metadata.get("decisionOption")
        if decision_option is not None:
            decision_option = FeasibilityStudyDecisionOption(decision_option["id"], decision_option["description"])
        return FeasibilityStudy(
            id=metadata["id"],
            created_at=metadata["createdAt"],
            updated_at=metadata["updatedAt"],
            account_id=metadata["accountId"],
            workspace_id=metadata["workspaceId"],
            order_id=metadata["orderId"],
            decision=metadata["decision"],
            options=metadata.get("options", []),
            decided_at=metadata.get("decisionAt"),
            decision_option=decision_option,
        )

    def accept(self, option_id: str):
        self.decision_option = FeasibilityStudyDecisionOption(option_id)

    def save(self):
        url = host.endpoint(f"/v2/tasking/feasibility-studies/{self.id}")
        if self.decision_option is None:
            raise FeasibilityStudy.NoDecisionOptionChosen(
                "No decision option chosen for this feasibility study. "
                "Please call 'accept' with a valid option ID before saving."
            )
        metadata = self.session.patch(url, json={"acceptedOptionId": self.decision_option.id}).json()
        feasibility_study = self._from_metadata(metadata)
        for field in dataclasses.fields(feasibility_study):
            setattr(self, field.name, getattr(feasibility_study, field.name))
