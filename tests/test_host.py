import pytest

from up42 import host

ENDPOINT = "https://api.up42.com/some-path"
SA_ENDPOINT = "https://api.sa.up42.com/some-path"
TOKEN_ENDPOINT = "https://auth.up42.com/realms/public/protocol/openid-connect/token"
SA_TOKEN_ENDPOINT = "https://auth.sa.up42.com/realms/public/protocol/openid-connect/token"
USER_INFO_ENDPOINT = "https://auth.up42.com/realms/public/protocol/openid-connect/userinfo"
SA_USER_INFO_ENDPOINT = "https://auth.sa.up42.com/realms/public/protocol/openid-connect/userinfo"


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

@pytest.mark.parametrize(
    "region, expected",
    [
        [
            "eu",
            ENDPOINT,
        ],
        [
            "sa",
            SA_ENDPOINT,
        ],
    ],
)
def test_should_use_correct_endpoint_url_for_requested_region(region, expected):
    host.REGION = region
    assert expected == host.endpoint("/some-path")


@pytest.mark.parametrize("region", ["xyz", "abc"])
def test_should_raise_an_error_when_retrieving_endpoint_for_unknown_region(region):
    host.REGION = region
    with pytest.raises(host.UnsupportedRegion):
        host.endpoint("/some-path")

@pytest.mark.parametrize(
    "region, expected",
    [
        [
            "eu",
            TOKEN_ENDPOINT,
        ],
        [
            "sa",
            SA_TOKEN_ENDPOINT,
        ],
    ],
)
def test_should_use_correct_token_endpoint_url_for_requested_region(region, expected):
    host.REGION = region
    assert expected == host.token_endpoint()


@pytest.mark.parametrize("region", ["xyz", "abc"])
def test_should_raise_an_error_when_retrieving_token_url_for_unknown_region(region):
    host.REGION = region
    with pytest.raises(host.UnsupportedRegion):
        host.token_endpoint()


@pytest.mark.parametrize(
    "region, expected",
    [
        [
            "eu",
            USER_INFO_ENDPOINT,
        ],
        [
            "sa",
            SA_USER_INFO_ENDPOINT,
        ],
    ],
)
def test_should_use_correct_userinfo_endpoint_url_for_requested_region(region, expected):
    host.REGION = region
    assert expected == host.user_info_endpoint()


@pytest.mark.parametrize("region", ["xyz", "abc"])
def test_should_raise_an_error_when_retrieving_userinfo_url_for_unknown_region(region):
    host.REGION = region
    with pytest.raises(host.UnsupportedRegion):
        host.user_info_endpoint()
