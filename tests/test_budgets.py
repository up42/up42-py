import random
import string
import urllib.parse
import uuid

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import budgets

BUDGET_ID = str(uuid.uuid4())
BUDGETS_URL = f"{constants.API_HOST}/v2/budgets"
BUDGET_URL = f"{BUDGETS_URL}/{BUDGET_ID}"


def random_alphanumeric():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


def random_metadata() -> dict:
    return {
        "id": BUDGET_ID,
        "name": random_alphanumeric(),
        "description": random_alphanumeric(),
        "externalId": random_alphanumeric(),
        "status": random.choice(["ACTIVE", "INACTIVE"]),
        "createdBy": random_alphanumeric(),
        "createdAt": random_alphanumeric(),
        "updatedAt": random_alphanumeric(),
    }


metadata = random_metadata()


@pytest.fixture(name="budget")
def _budget():
    return budgets.Budget(
        id=metadata["id"],
        name=metadata["name"],
        description=metadata["description"],
        external_id=metadata["externalId"],
        status=metadata["status"],
        created_by=metadata["createdBy"],
        created_at=metadata["createdAt"],
        updated_at=metadata["updatedAt"],
    )


class TestBudget:
    def test_should_get_budget(self, requests_mock: req_mock.Mocker, budget: budgets.Budget):
        requests_mock.get(url=BUDGET_URL, json={"data": metadata})
        assert budgets.Budget.get(BUDGET_ID) == budget

    @pytest.mark.parametrize(
        "response_metadata",
        [
            {
                "id": BUDGET_ID,
                "name": "some-name",
                "status": "ACTIVE",
                "createdBy": "user",
                "createdAt": "2026-01-01",
                "updatedAt": "2026-01-02",
            },
            {
                "id": BUDGET_ID,
                "name": "some-name",
                "description": None,
                "externalId": None,
                "status": "ACTIVE",
                "createdBy": "user",
                "createdAt": "2026-01-01",
                "updatedAt": "2026-01-02",
            },
        ],
        ids=["missing_keys", "explicit_nulls"],
    )
    def test_should_handle_null_optional_fields(
        self, requests_mock: req_mock.Mocker, response_metadata: dict
    ):
        requests_mock.get(url=BUDGET_URL, json={"data": response_metadata})
        result = budgets.Budget.get(BUDGET_ID)
        assert result.description is None
        assert result.external_id is None

    def test_should_create(self, requests_mock: req_mock.Mocker):
        response_data = metadata.copy()
        requests_mock.post(
            BUDGETS_URL,
            json={"data": response_data},
        )
        created = budgets.Budget.create(
            name=metadata["name"],
            description=metadata["description"],
            external_id=metadata["externalId"],
            status=metadata["status"],
        )
        assert created.id == metadata["id"]
        assert created.name == metadata["name"]
        assert created.created_by == metadata["createdBy"]
        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "name": metadata["name"],
            "description": metadata["description"],
            "externalId": metadata["externalId"],
            "status": metadata["status"],
        }

    def test_should_save(self, requests_mock: req_mock.Mocker, budget: budgets.Budget):
        budget.name = "new-name"
        budget.description = "new-description"
        budget.external_id = "new-external-id"
        budget.status = "INACTIVE"
        updated_at = "new-updated-at"
        requests_mock.put(BUDGET_URL, json={"data": {"updatedAt": updated_at}})
        budget.save()
        assert budget.updated_at == updated_at
        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "name": "new-name",
            "description": "new-description",
            "externalId": "new-external-id",
            "status": "INACTIVE",
        }

    def test_save_should_raise_without_id(self, budget: budgets.Budget):
        budget.id = ""
        with pytest.raises(ValueError, match="Cannot save a budget without an id"):
            budget.save()

    @pytest.mark.parametrize(
        "status,sort_by",
        [
            (None, None),
            (["ACTIVE"], None),
            (None, budgets.BudgetSorting.updated_at),
            (["ACTIVE", "INACTIVE"], budgets.BudgetSorting.updated_at),
        ],
        ids=["no_filters", "status_filter", "sort_only", "status_and_sort"],
    )
    def test_should_get_all_budgets(
        self,
        status: list[str] | None,
        sort_by: budgets.BudgetSorting | None,
        requests_mock: req_mock.Mocker,
        budget: budgets.Budget,
    ):
        query_params: dict = {"page": 0}
        if status:
            query_params["status"] = status
        if sort_by:
            query_params["sort"] = str(sort_by)
        query = urllib.parse.urlencode(query_params, doseq=True)
        response = {"content": [metadata], "totalPages": 1}
        requests_mock.get(url=f"{BUDGETS_URL}?{query}", json=response)
        assert list(budgets.Budget.all(status=status, sort_by=sort_by)) == [budget]

    def test_should_get_usage(self, requests_mock: req_mock.Mocker, budget: budgets.Budget):
        usage_metadata = {
            "budgetId": BUDGET_ID,
            "consumedCredits": 42,
        }
        url = f"{BUDGET_URL}/usage"
        requests_mock.get(url=url, json={"data": usage_metadata})
        usage = budget.get_usage()
        assert usage == budgets.BudgetUsage(budget_id=BUDGET_ID, consumed_credits=42)

    def test_should_get_settings(self, requests_mock: req_mock.Mocker):
        settings_metadata = {
            "enforcementEnabled": True,
            "budgetSettingId": "setting-123",
        }
        url = f"{BUDGETS_URL}/settings"
        requests_mock.get(url=url, json={"data": settings_metadata})
        settings = budgets.BudgetSettings.get()
        assert settings == budgets.BudgetSettings(
            enforcement_enabled=True, budget_settings_id="setting-123"
        )

    def test_should_update_settings(self, requests_mock: req_mock.Mocker):
        settings_metadata = {
            "enforcementEnabled": False,
            "budgetSettingId": "setting-456",
        }
        url = f"{BUDGETS_URL}/settings"
        requests_mock.patch(url=url, json={"data": settings_metadata})
        settings = budgets.BudgetSettings.update(enforcement_enabled=False)
        assert settings == budgets.BudgetSettings(
            enforcement_enabled=False, budget_settings_id="setting-456"
        )
        assert requests_mock.last_request and requests_mock.last_request.json() == {
            "enforcementEnabled": False,
        }

