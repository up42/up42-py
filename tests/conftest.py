import pytest

from up42 import host

pytest_plugins = [
    "tests.fixtures.fixtures_auth",
    "tests.fixtures.fixtures_storage",
]


@pytest.fixture(autouse=True)
def restore_default_domain():
    # To avoid breaking urls in other tests when the domain is changed in a test
    default_domain = host.DOMAIN
    yield
    host.DOMAIN = default_domain
