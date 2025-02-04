import pytest

from up42 import host


@pytest.mark.parametrize("domain", ["xyz", "abc"])
def test_should_use_domain_in_endpoint_url(domain):
    host.DOMAIN = domain
    assert host.endpoint("/path") == f"https://api.up42.{domain}/path"


@pytest.mark.parametrize("domain", ["xyz", "abc"])
def test_should_use_domain_in_token_endpoint_url(domain):
    host.DOMAIN = domain
    assert domain in host.token_endpoint()


@pytest.mark.parametrize("domain", ["xyz", "abc"])
def test_should_use_domain_in_user_info_endpoint_url(domain):
    host.DOMAIN = domain
    assert domain in host.user_info_endpoint()
