import dataclasses
from collections.abc import Iterator
from typing import Literal, TypeAlias

from up42 import base, host, utils

logger = utils.get_logger(__name__)

BudgetStatus: TypeAlias = Literal[
    "ACTIVE",
    "INACTIVE",
]


class BudgetSorting:
    updated_at = utils.SortingField(name="updatedAt")


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

    @classmethod
    def create(
        cls,
        name: str,
        status: BudgetStatus,
        description: str | None = None,
        external_id: str | None = None,
    ) -> "Budget":
        url = host.endpoint("/v2/budgets")
        payload = {
            "name": name,
            "description": description,
            "externalId": external_id,
            "status": status,
        }
        response_json = cls.session.post(url=url, json=payload).json()["data"]
        logger.info("Created budget %s", response_json["id"])
        return cls._from_metadata(response_json)

    def save(self):
        if not self.id:
            raise ValueError(
                "Cannot save a budget without an id. Use Budget.create() to create a new budget."
            )
        url = host.endpoint(f"/v2/budgets/{self.id}")
        payload = {
            "name": self.name,
            "description": self.description,
            "externalId": self.external_id,
            "status": self.status,
        }
        response_json = self.session.put(url=url, json=payload).json()["data"]
        self.updated_at = response_json["updatedAt"]
        logger.info("Saved budget %s", self.id)

    @staticmethod
    def _from_metadata(metadata: dict) -> "Budget":
        return Budget(
            id=metadata["id"],
            name=metadata["name"],
            description=metadata.get("description"),
            external_id=metadata.get("externalId"),
            status=metadata["status"],
            created_by=metadata["createdBy"],
            created_at=metadata["createdAt"],
            updated_at=metadata["updatedAt"],
        )

    @classmethod
    def get(cls, budget_id: str) -> "Budget":
        url = host.endpoint(f"/v2/budgets/{budget_id}")
        logger.debug("Fetching budget %s", budget_id)
        metadata = cls.session.get(url).json()["data"]
        return cls._from_metadata(metadata)

    @classmethod
    def all(
        cls,
        status: list[BudgetStatus] | None = None,
        sort_by: utils.SortingField | None = None,
    ) -> Iterator["Budget"]:
        logger.debug("Listing budgets with status=%s, sort_by=%s", status, sort_by)
        params = {
            "sort": sort_by,
            "status": status,
        }
        return map(
            cls._from_metadata,
            utils.paged_query(params, "/v2/budgets", cls.session),
        )

    def get_usage(self) -> "BudgetUsage":
        url = host.endpoint(f"/v2/budgets/{self.id}/usage")
        logger.debug("Fetching usage for budget %s", self.id)
        metadata = self.session.get(url).json()["data"]
        return BudgetUsage.from_metadata(metadata)


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


@dataclasses.dataclass
class BudgetSettings:
    session = base.Session()
    enforcement_enabled: bool
    budget_settings_id: str | None

    @staticmethod
    def _from_metadata(metadata: dict) -> "BudgetSettings":
        return BudgetSettings(
            enforcement_enabled=metadata["enforcementEnabled"],
            budget_settings_id=metadata.get("budgetSettingId"),
        )

    @classmethod
    def get(cls) -> "BudgetSettings":
        url = host.endpoint("/v2/budgets/settings")
        logger.debug("Fetching budget settings")
        metadata = cls.session.get(url).json()["data"]
        return cls._from_metadata(metadata)

    @classmethod
    def update(cls, enforcement_enabled: bool) -> "BudgetSettings":
        url = host.endpoint("/v2/budgets/settings")
        payload = {
            "enforcementEnabled": enforcement_enabled,
        }
        metadata = cls.session.patch(url=url, json=payload).json()["data"]
        logger.info(
            "Updated budget settings: enforcement_enabled=%s", enforcement_enabled
        )
        return cls._from_metadata(metadata)
