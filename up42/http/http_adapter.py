from typing import Callable

from requests import adapters
from urllib3 import util

from up42.http import config


def create(
    supply_settings: Callable[[], config.ResilienceSettings] = config.ResilienceSettings, include_post: bool = False
) -> adapters.HTTPAdapter:
    settings = supply_settings()
    allowed_methods = set(util.Retry.DEFAULT_ALLOWED_METHODS)
    if include_post:
        allowed_methods.add("POST")

    retries = util.Retry(
        total=settings.total,
        backoff_factor=settings.backoff_factor,
        status_forcelist=settings.statuses,
        allowed_methods=allowed_methods,
    )
    return adapters.HTTPAdapter(max_retries=retries)
