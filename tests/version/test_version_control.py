import random
from unittest import mock

import pytest
import requests_mock as req_mock
from packaging import version

from up42.version import version_control

fake_latest_version = "10.0.0"
fake_installed_version = "1.0.0"


class TestBuildMessage:
    def test_should_build_warn_message(self):
        assert (
            version_control.build_outdated_version_message(fake_installed_version, fake_latest_version)
            == f"You're using an outdated version of the UP42 Python SDK: v{fake_installed_version}. A newer version is available: v{fake_latest_version}.\nPlease upgrade to the latest version using **pip install --upgrade up42-py** or conda **conda update -c conda-forge up42-py**."  # pylint: disable=line-too-long # noqa: E501
        )


class TestCheckLatestVersion:
    def test_should_warn_if_not_latest_version(
        self,
        requests_mock: req_mock.Mocker,
    ):
        warn = mock.MagicMock()
        requests_mock.get(url="https://pypi.org/pypi/up42-py/json", json={"info": {"version": fake_latest_version}})
        message = "not latest version"
        build_warning_message = mock.MagicMock(return_value=message)
        version_control.check_is_latest_version(fake_installed_version, warn, build_warning_message)
        build_warning_message.assert_called_with(fake_installed_version, version.Version(fake_latest_version))
        warn.assert_called_with(message)

    def test_should_ignore_http_error_exception(
        self,
        requests_mock: req_mock.Mocker,
    ):
        requests_mock.get(url="https://pypi.org/pypi/up42-py/json", status_code=random.randint(400, 599))
        unused = mock.MagicMock()
        version_control.check_is_latest_version(fake_installed_version, unused, unused)
        unused.assert_not_called()

    def test_should_not_check_the_version_if_the_env_variable_is_set_to_true(self):
        warn = mock.MagicMock()
        check_latest_version = mock.MagicMock(return_value=False)
        version_control.check_is_latest_version(
            fake_installed_version, warn=warn, check_latest_version=check_latest_version
        )
        warn.assert_not_called()


class TestIsLatestVersionCheckEnabled:
    @staticmethod
    def _get_fake_getenv(value):
        def _getenv(name):  # pylint: disable=unused-argument
            return value

        return _getenv

    @pytest.mark.parametrize(
        "env_value, expected_result",
        [
            (None, True),
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
        ],
    )
    def test_should_return_correct_boolean_for_valid_values(self, env_value, expected_result):
        assert version_control.is_latest_version_check_enabled(self._get_fake_getenv(env_value)) is expected_result

    @pytest.mark.parametrize("env_value", ["1", "0", "yes", "no", "random", ""])
    def test_should_raise_value_error_for_invalid_values(self, env_value):
        with pytest.raises(ValueError, match="must be a bool"):
            version_control.is_latest_version_check_enabled(self._get_fake_getenv(env_value))
