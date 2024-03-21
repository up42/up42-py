import pytest

from up42 import host


@pytest.mark.parametrize("domain", ["xyz", "abc"])
def test_should_use_domain_in_endpoint_url(domain):
    host.DOMAIN = domain
    assert host.endpoint("/path") == f"https://api.up42.{domain}/path"
