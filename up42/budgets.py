import dataclasses
from collections.abc import Iterator
from typing import Literal, TypeAlias

from up42 import base, host, utils

BudgetStatus: TypeAlias = Literal[
    "ACTIVE",
    "INACTIVE",
]


class BudgetSorting:
    updated_at = utils.SortingField(name="updatedAt")


@dataclasses.dataclass
class ValidityPeriod:
    start_date: str
    end_date: str

    @staticmethod
    def from_metadata(metadata: dict) -> "ValidityPeriod":
        return ValidityPeriod(
            start_date=metadata["startDate"],
            end_date=metadata["endDate"],
        )


@dataclasses.dataclass
class Budget:
    session = base.Session()
    id: str
    name: str
    status: BudgetStatus
    created_by: str
    created_at: str
    updated_at: str

    description: str | None = None
    external_id: str | None = None

    spend_limit: int | None = None
    validity_period: ValidityPeriod | None = None

    consumed_credits: int | None = None
    remaining_credits: int | None = None
    usage_percentage: float | None = None

    @staticmethod
    def _from_metadata(metadata: dict) -> "Budget":
        validity_period = metadata.get("validityPeriod")
        return Budget(
            id=metadata["id"],
            name=metadata["name"],
            description=metadata.get("description"),
            external_id=metadata.get("externalId"),
            status=metadata["status"],
            created_by=metadata["createdBy"],
            created_at=metadata["createdAt"],
            updated_at=metadata["updatedAt"],
            spend_limit=metadata.get("spendLimit"),
            validity_period=ValidityPeriod.from_metadata(validity_period)
            if validity_period
            else None,
            consumed_credits=metadata.get("consumedCredits"),
            remaining_credits=metadata.get("remainingCredits"),
            usage_percentage=metadata.get("usagePercentage"),
        )

    @classmethod
    def get(cls, budget_id: str, include_usage: bool = False) -> "Budget":
        url = host.endpoint(f"/v2/budgets/{budget_id}")
        metadata = cls.session.get(
            url, params={"includeUsage": include_usage}
        ).json()
        return cls._from_metadata(metadata)

    @classmethod
    def all(
        cls,
        status: list[BudgetStatus] | None = None,
        sort_by: utils.SortingField | None = None,
        include_usage: bool = False,
    ) -> Iterator["Budget"]:
        params = {
            "sort": sort_by,
            "status": status,
            "includeUsage": include_usage,
        }
        return map(
            cls._from_metadata,
            utils.paged_query(params, "/v2/budgets", cls.session),
        )

    def get_usage(self) -> "BudgetUsage":
        url = host.endpoint(f"/v2/budgets/{self.id}/usage")
        metadata = self.session.get(url).json()
        return BudgetUsage.from_metadata(metadata)


@dataclasses.dataclass
class BudgetSettings:
    session = base.Session()
    enforcement_enabled: bool
    budget_setting_id: str | None = None

    @staticmethod
    def _from_metadata(metadata: dict) -> "BudgetSettings":
        return BudgetSettings(
            enforcement_enabled=metadata["enforcementEnabled"],
            budget_setting_id=metadata.get("budgetSettingId"),
        )

    @classmethod
    def get(cls) -> "BudgetSettings":
        url = host.endpoint("/v2/budgets/settings")
        metadata = cls.session.get(url).json()
        return cls._from_metadata(metadata)


@dataclasses.dataclass
class BudgetUsage:
    budget_id: str
    consumed_credits: int

    @staticmethod
    def from_metadata(metadata: dict) -> "BudgetUsage":
        return BudgetUsage(
            budget_id=metadata["budgetId"],
            consumed_credits=metadata["consumedCredits"],
        )
