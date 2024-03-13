import pytest

from up42 import host

pytest_plugins = [
    "tests.fixtures.fixtures_auth",
    "tests.fixtures.fixtures_asset",
    "tests.fixtures.fixtures_catalog",
    "tests.fixtures.fixtures_estimation",
    "tests.fixtures.fixtures_job",
    "tests.fixtures.fixtures_jobcollection",
    "tests.fixtures.fixtures_jobtask",
    "tests.fixtures.fixtures_order",
    "tests.fixtures.fixtures_project",
    "tests.fixtures.fixtures_storage",
    "tests.fixtures.fixtures_tasking",
    "tests.fixtures.fixtures_webhook",
    "tests.fixtures.fixtures_workflow",
]


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
