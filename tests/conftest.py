import pytest

from up42 import host

from .fixtures.fixtures_asset import asset_live, asset_mock, asset_mock2, assets_fixture
from .fixtures.fixtures_auth import (
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    setup_auth_mock,
    username_test_live,
)
from .fixtures.fixtures_catalog import catalog_live, catalog_mock, catalog_pagination_mock, catalog_usagetype_mock
from .fixtures.fixtures_estimation import estimation_live, estimation_mock
from .fixtures.fixtures_job import job_live, job_mock, jobs_live, jobs_mock
from .fixtures.fixtures_jobcollection import (
    jobcollection_empty_mock,
    jobcollection_live,
    jobcollection_multiple_mock,
    jobcollection_single_mock,
)
from .fixtures.fixtures_jobtask import jobtask_live, jobtask_mock
from .fixtures.fixtures_order import (
    catalog_order_parameters,
    order_live,
    order_mock,
    order_parameters,
    tasking_order_parameters,
)
from .fixtures.fixtures_project import project_live, project_mock, project_mock_max_concurrent_jobs
from .fixtures.fixtures_storage import storage_live, storage_mock
from .fixtures.fixtures_tasking import (
    tasking_choose_feasibility_mock,
    tasking_get_feasibility_mock,
    tasking_live,
    tasking_mock,
)
from .fixtures.fixtures_webhook import webhook_live, webhook_mock, webhooks_live, webhooks_mock
from .fixtures.fixtures_workflow import workflow_live, workflow_mock, workflow_mock_empty


@pytest.fixture(autouse=True)
def restore_default_domain():
    # To avoid breaking urls in other tests when the domain is changed in a test
    default_domain = host.DOMAIN
    yield
    host.DOMAIN = default_domain


def pytest_addoption(parser):
    parser.addoption("--runlive", action="store_true", default=False, help="run live tests")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--runlive"):
        skip_live = pytest.mark.skip(reason="need --runlive option to run")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)
