import random

import pytest

from up42.http.config import ResilienceSettings
from up42.http.http_adapter import create as create_adapter


@pytest.mark.parametrize("include_post", [True, False])
def test_should_create_adapter(include_post):
    total_retries = 5
    backoff_factor = 0.4
    statuses = (random.randint(400, 600),)
    settings = ResilienceSettings(total=total_retries, backoff_factor=backoff_factor, statuses=statuses)
    adapter = create_adapter(supply_settings=lambda: settings, include_post=include_post)
    assert adapter.max_retries.total == total_retries
    assert adapter.max_retries.backoff_factor == backoff_factor
    assert adapter.max_retries.status_forcelist == statuses
    allowed_methods = adapter.max_retries.allowed_methods or []
    if include_post:
        assert "POST" in allowed_methods
    else:
        assert "POST" not in allowed_methods
