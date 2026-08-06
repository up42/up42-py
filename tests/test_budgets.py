import random
import string
import urllib.parse
import uuid

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import budgets, utils

BUDGET_ID = str(uuid.uuid4())
BUDGETS_URL = f"{constants.API_HOST}/v2/budgets"
BUDGET_URL = f"{BUDGETS_URL}/{BUDGET_ID}"
BUDGET_SETTINGS_URL = f"{BUDGETS_URL}/settings"


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
    def test_should_get_budget(
        self, requests_mock: req_mock.Mocker, budget: budgets.Budget
    ):
        requests_mock.get(url=BUDGET_URL, json=metadata)
        assert budgets.Budget.get(BUDGET_ID) == budget

    @pytest.mark.parametrize(
        "response_metadata",
        [
            {
                "id": BUDGET_ID,
                "name": "some-name",
                "status": "ACTIVE",
                "createdBy": "68567134-27ad-7bd7-4b65-d61adb11fc78",
                "createdAt": "2026-01-01",
                "updatedAt": "2026-01-02",
            },
            {
                "id": BUDGET_ID,
                "name": "some-name",
                "description": None,
                "externalId": None,
                "status": "ACTIVE",
                "createdBy": "68567134-27ad-7bd7-4b65-d61adb11fc78",
                "createdAt": "2026-01-01",
                "updatedAt": "2026-01-02",
            },
        ],
        ids=["missing_keys", "explicit_nulls"],
    )
    def test_should_handle_null_optional_fields(
        self, requests_mock: req_mock.Mocker, response_metadata: dict
    ):
        requests_mock.get(url=BUDGET_URL, json=response_metadata)
        result = budgets.Budget.get(BUDGET_ID)
        assert result.description is None
        assert result.external_id is None

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
        status: list[budgets.BudgetStatus] | None,
        sort_by: utils.SortingField | None,
        requests_mock: req_mock.Mocker,
        budget: budgets.Budget,
    ):
        query_params: dict = {}
        if sort_by:
            query_params["sort"] = str(sort_by)
        if status:
            query_params["status"] = status
        query_params["page"] = 0
        query = urllib.parse.urlencode(query_params, doseq=True, safe="")
        response = {"content": [metadata], "totalPages": 1}
        url = BUDGETS_URL + (query and f"?{query}")
        requests_mock.get(url=url, json=response)
        assert list(budgets.Budget.all(status=status, sort_by=sort_by)) == [
            budget
        ]

    def test_should_get_usage(
        self, requests_mock: req_mock.Mocker, budget: budgets.Budget
    ):
        usage_metadata = {
            "budgetId": BUDGET_ID,
            "consumedCredits": 42,
        }
        url = f"{BUDGET_URL}/usage"
        requests_mock.get(url=url, json=usage_metadata)
        usage = budget.get_usage()
        assert usage == budgets.BudgetUsage(
            budget_id=BUDGET_ID, consumed_credits=42
        )


class TestBudgetSettings:
    def test_should_get_budget_settings(self, requests_mock: req_mock.Mocker):
        budget_setting_id = str(uuid.uuid4())
        response = {
            "budgetSettingId": budget_setting_id,
            "enforcementEnabled": True,
        }
        requests_mock.get(url=BUDGET_SETTINGS_URL, json=response)
        assert budgets.BudgetSettings.get() == budgets.BudgetSettings(
            budget_setting_id=budget_setting_id,
            enforcement_enabled=True,
        )

    @pytest.mark.parametrize(
        "response_metadata",
        [
            {"enforcementEnabled": False},
            {"budgetSettingId": None, "enforcementEnabled": False},
        ],
        ids=["missing_budget_setting_id", "explicit_null_budget_setting_id"],
    )
    def test_should_handle_null_budget_setting_id(
        self, requests_mock: req_mock.Mocker, response_metadata: dict
    ):
        requests_mock.get(url=BUDGET_SETTINGS_URL, json=response_metadata)
        result = budgets.BudgetSettings.get()
        assert result.budget_setting_id is None
        assert result.enforcement_enabled is False
