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
        is_version_check_enabled = mock.MagicMock(return_value=True)
        version_control.check_is_latest_version(
            fake_installed_version,
            warn=warn,
            build_warning_message=build_warning_message,
            is_version_check_enabled=is_version_check_enabled,
        )
        build_warning_message.assert_called_with(fake_installed_version, version.Version(fake_latest_version))
        warn.assert_called_with(message)

    def test_should_ignore_http_error_exception(
        self,
        requests_mock: req_mock.Mocker,
    ):
        requests_mock.get(url="https://pypi.org/pypi/up42-py/json", status_code=random.randint(400, 599))
        unused = mock.MagicMock()
        is_version_check_enabled = mock.MagicMock(return_value=True)
        version_control.check_is_latest_version(
            fake_installed_version,
            warn=unused,
            build_warning_message=unused,
            is_version_check_enabled=is_version_check_enabled,
        )
        unused.assert_not_called()

    def test_should_not_check_the_version_if_latest_version_check_is_disabled(self):
        unused = mock.MagicMock()
        is_version_enabled = mock.MagicMock(return_value=False)
        version_control.check_is_latest_version(
            fake_installed_version,
            warn=unused,
            build_warning_message=unused,
            is_version_check_enabled=is_version_enabled,
        )
        unused.assert_not_called()


class TestIsLatestVersionCheckEnabled:
    @pytest.mark.parametrize(
        "env_var, expected_result",
        [
            (None, True),
            ("False", True),
            ("True", False),
        ],
    )
    def test_should_return_correct_boolean_for_valid_values(self, env_var, expected_result):
        get_env_var = mock.MagicMock(return_value=env_var)
        assert version_control.is_latest_version_check_enabled(get_environment_variable=get_env_var) is expected_result

    def test_should_raise_value_error_for_invalid_values(self):
        get_env_var = mock.MagicMock(return_value="no_boolean")
        with pytest.raises(
            ValueError,
            match="UP42_DISABLE_VERSION_CHECK is a boolean environment variable, so it must be either "
            + f"'True' or 'False', got '{get_env_var()}'.",
        ):
            version_control.is_latest_version_check_enabled(get_environment_variable=get_env_var)
