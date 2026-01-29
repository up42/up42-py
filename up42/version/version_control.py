import functools
import logging
import os
import warnings

import requests
from packaging import version

DISABLE_VERSION_CHECK_ENVIRONMENT_VARIABLE = "UP42_DISABLE_VERSION_CHECK"

TRUE_VALUES = ("TRUE", "True", "true", "T", "t", "1")


def should_check_version():
    return os.getenv(DISABLE_VERSION_CHECK_ENVIRONMENT_VARIABLE) not in TRUE_VALUES


def _get_latest_version():
    response = requests.get("https://pypi.org/pypi/up42-py/json", timeout=2)
    response.raise_for_status()
    return version.parse(response.json()["info"]["version"])


def build_outdated_version_message(installed_version, latest_version):
    return f"You're using an outdated version of the UP42 Python SDK: v{installed_version}. A newer version is available: v{latest_version}.\nPlease upgrade to the latest version using **pip install --upgrade up42-py** or conda **conda update -c conda-forge up42-py**."  # pylint: disable=line-too-long # noqa: E501


@functools.lru_cache
def check_is_latest_version(
    installed_version: str,
    warn=warnings.warn,
    build_warning_message=build_outdated_version_message,
):
    try:
        if should_check_version():
            latest_version = _get_latest_version()
            if version.Version(installed_version) < latest_version:
                warn(build_warning_message(installed_version, latest_version))
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logging.error("Failed to check latest version", exc_info=exc)
        pass
