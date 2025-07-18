import warnings

import requests
from packaging import version
from requests import exceptions


def _get_latest_version():
    response = requests.get("https://pypi.org/pypi/up42-py/json", timeout=2)
    response.raise_for_status()
    return version.parse(response.json()["info"]["version"])


def build_outdated_version_message(installed_version, latest_version):
    return f"You're using an outdated version of the UP42 Python SDK: v{installed_version}. A newer version is available: v{latest_version}.\nPlease upgrade to the latest version using **pip install --upgrade up42-py** or conda **conda update -c conda-forge up42-py**."  # pylint: disable=line-too-long # noqa: E501


def check_is_latest_version(
    installed_version,
    warn=warnings.warn,
    build_warning_message=build_outdated_version_message,
):
    try:
        latest_version = _get_latest_version()
        if installed_version < latest_version:
            warn(build_warning_message(installed_version, latest_version))
    except exceptions.HTTPError:
        pass
