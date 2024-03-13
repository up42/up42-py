from typing import Dict, List, Optional
from unittest import mock

import pytest

from up42.http import client

CONFIG_FILE = "some-config"
SETTINGS_SOURCE = {"some": "settings"}
CONFIG_CREDENTIALS = {"project_id": "some-id", "password": "some-pass"}
PROJECT_CREDENTIALS = {"project_id": "some-id", "project_api_key": "some-key"}
ACCOUNT_CREDENTIALS = {"username": "some-user", "password": "some-pass"}
EMPTY_PROJECT_CREDENTIALS = {"project_id": None, "project_api_key": None}
EMPTY_ACCOUNT_CREDENTIALS = {"username": None, "password": None}


class TestMergeSettings:
    @pytest.mark.parametrize(
        "config, project_settings, account_settings, detected_settings",
        [
            [CONFIG_CREDENTIALS, EMPTY_PROJECT_CREDENTIALS, EMPTY_ACCOUNT_CREDENTIALS, [SETTINGS_SOURCE, None, None]],
            [None, PROJECT_CREDENTIALS, EMPTY_ACCOUNT_CREDENTIALS, [None, SETTINGS_SOURCE, None]],
            [None, EMPTY_PROJECT_CREDENTIALS, ACCOUNT_CREDENTIALS, [None, None, SETTINGS_SOURCE]],
        ],
    )
    def test_should_merge_if_only_one_source_is_given(
        self,
        config: Optional[dict],
        project_settings: dict,
        account_settings: dict,
        detected_settings: List[Optional[Dict]],
    ):
        read_config = mock.MagicMock(return_value=config)
        detect_settings = mock.MagicMock(side_effect=detected_settings)
        assert (
            client.merge_settings(
                CONFIG_FILE,
                **project_settings,
                **account_settings,
                read_config=read_config,
                detect_settings=detect_settings,
            )
            == SETTINGS_SOURCE
        )
        read_config.assert_called_with(CONFIG_FILE)
        detect_settings.assert_has_calls(
            [
                mock.call(config or {}),
                mock.call(project_settings),
                mock.call(account_settings),
            ]
        )

    @pytest.mark.parametrize(
        "config, project_settings, account_settings, detected_settings",
        [
            [
                CONFIG_CREDENTIALS,
                PROJECT_CREDENTIALS,
                EMPTY_ACCOUNT_CREDENTIALS,
                [SETTINGS_SOURCE, SETTINGS_SOURCE, None],
            ],
            [None, PROJECT_CREDENTIALS, ACCOUNT_CREDENTIALS, [None, SETTINGS_SOURCE, SETTINGS_SOURCE]],
            [
                CONFIG_CREDENTIALS,
                EMPTY_PROJECT_CREDENTIALS,
                ACCOUNT_CREDENTIALS,
                [SETTINGS_SOURCE, None, SETTINGS_SOURCE],
            ],
            [
                CONFIG_CREDENTIALS,
                PROJECT_CREDENTIALS,
                ACCOUNT_CREDENTIALS,
                [SETTINGS_SOURCE, SETTINGS_SOURCE, SETTINGS_SOURCE],
            ],
        ],
    )
    def test_fails_to_merge_if_multiple_sources_are_given(
        self,
        config: Optional[dict],
        project_settings: dict,
        account_settings: dict,
        detected_settings: List[Optional[Dict]],
    ):
        read_config = mock.MagicMock(return_value=config)
        detect_settings = mock.MagicMock(side_effect=detected_settings)
        with pytest.raises(client.MultipleCredentialsSources):
            client.merge_settings(
                CONFIG_FILE,
                **project_settings,
                **account_settings,
                read_config=read_config,
                detect_settings=detect_settings,
            )
        read_config.assert_called_with(CONFIG_FILE)
        detect_settings.assert_has_calls(
            [
                mock.call(config or {}),
                mock.call(project_settings),
                mock.call(account_settings),
            ]
        )

    @pytest.mark.parametrize("config", [{}, None])
    def test_fails_to_merge_if_no_source_is_given(self, config: Optional[dict]):
        read_config = mock.MagicMock(return_value=config)
        detect_settings = mock.MagicMock(return_value=None)
        with pytest.raises(client.MissingCredentials):
            client.merge_settings(
                CONFIG_FILE,
                **EMPTY_PROJECT_CREDENTIALS,
                **EMPTY_ACCOUNT_CREDENTIALS,
                read_config=read_config,
                detect_settings=detect_settings,
            )
        read_config.assert_called_with(CONFIG_FILE)
        detect_settings.assert_has_calls(
            [
                mock.call(config or {}),
                mock.call(EMPTY_PROJECT_CREDENTIALS),
                mock.call(EMPTY_ACCOUNT_CREDENTIALS),
            ]
        )


class TestCreate:
    def test_should_create_client(self):
        get_settings = mock.MagicMock(return_value=SETTINGS_SOURCE)
        access_token = "some-token"
        retrieve = mock.sentinel.some_object
        detect_retriever = mock.MagicMock(return_value=retrieve)
        auth = mock.MagicMock()
        auth.token.access_token = access_token
        create_auth = mock.MagicMock(return_value=auth)
        result = client.create(
            CONFIG_FILE,
            **PROJECT_CREDENTIALS,
            **ACCOUNT_CREDENTIALS,
            get_settings=get_settings,
            detect_retriever=detect_retriever,
            create_auth=create_auth,
        )
        assert result.token == access_token
        detect_retriever.assert_called_with(SETTINGS_SOURCE)
        create_auth.assert_called_with(retrieve)
