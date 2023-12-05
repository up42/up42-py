import pytest

from up42 import host


@pytest.fixture(autouse=True)
def restore_default_domain():
    # The restoration of the default domain value is needed
    # to avoid breaking urls in other tests when domain is changed in a test
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
