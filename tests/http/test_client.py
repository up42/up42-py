from typing import Dict, List, Optional
from unittest import mock

import pytest

from up42.http import client

SETTINGS = {"some": "settings"}
PROJECT_CREDENTIALS = {"project_id": "some-id", "project_api_key": "some-key"}
ACCOUNT_CREDENTIALS = {"username": "some-user", "password": "some-pass"}
EMPTY_PROJECT_CREDENTIALS = {"project_id": None, "project_api_key": None}
EMPTY_ACCOUNT_CREDENTIALS = {"username": None, "password": None}


class TestCreate:
    unreachable = mock.MagicMock()

    @pytest.mark.parametrize(
        "project_settings, account_settings, detected_settings",
        [
            [EMPTY_PROJECT_CREDENTIALS, ACCOUNT_CREDENTIALS, [None, SETTINGS]],
            [PROJECT_CREDENTIALS, EMPTY_ACCOUNT_CREDENTIALS, [SETTINGS, None]],
        ],
    )
    def test_should_create_if_only_one_source_is_given(
        self,
        project_settings: dict,
        account_settings: dict,
        detected_settings: List[Optional[Dict]],
    ):
        detect_settings = mock.MagicMock(side_effect=detected_settings)
        access_token = "some-token"
        retrieve = mock.sentinel.some_object
        detect_retriever = mock.MagicMock(return_value=retrieve)
        auth = mock.MagicMock()
        auth.token.access_token = access_token
        create_auth = mock.MagicMock(return_value=auth)
        result = client.create(
            [project_settings, account_settings],
            detect_settings=detect_settings,
            detect_retriever=detect_retriever,
            create_auth=create_auth,
        )
        assert result.token == access_token
        detect_settings.assert_has_calls(
            [
                mock.call(project_settings),
                mock.call(account_settings),
            ]
        )
        detect_retriever.assert_called_with(SETTINGS)
        create_auth.assert_called_with(retrieve)

    def test_fails_to_create_if_multiple_sources_are_given(self):
        detect_settings = mock.MagicMock(return_value=SETTINGS)
        with pytest.raises(client.MultipleCredentialsSources):
            client.create(
                credential_sources=[PROJECT_CREDENTIALS, ACCOUNT_CREDENTIALS],
                detect_settings=detect_settings,
                detect_retriever=self.unreachable,
                create_auth=self.unreachable,
            )
        detect_settings.assert_has_calls(
            [
                mock.call(PROJECT_CREDENTIALS),
                mock.call(ACCOUNT_CREDENTIALS),
            ]
        )
        self.unreachable.assert_not_called()

    def test_fails_to_merge_if_no_source_is_given(self):
        detect_settings = mock.MagicMock(return_value=None)
        with pytest.raises(client.MissingCredentials):
            client.create(
                credential_sources=[EMPTY_PROJECT_CREDENTIALS, EMPTY_ACCOUNT_CREDENTIALS],
                detect_settings=detect_settings,
                detect_retriever=self.unreachable,
                create_auth=self.unreachable,
            )
        detect_settings.assert_has_calls(
            [
                mock.call(EMPTY_PROJECT_CREDENTIALS),
                mock.call(EMPTY_ACCOUNT_CREDENTIALS),
            ]
        )
        self.unreachable.assert_not_called()
