from typing import Dict, List, Optional, Type
from unittest import mock

import pytest

from tests import constants
from up42.http import client, config

SETTINGS = {"some": "settings"}
ACCOUNT_CREDENTIALS = {"username": "some-user", "password": "some-pass"}
EMPTY_ACCOUNT_CREDENTIALS = {"username": None, "password": None}
TOKEN_URL = "some-token-url"
CONFIG_FILE = "some-config-file"
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {constants.TOKEN}",
    "custom": "header",
}


class TestCreate:
    unreachable = mock.MagicMock()

    @pytest.mark.parametrize(
        "sources, detected_settings",
        [
            [[EMPTY_ACCOUNT_CREDENTIALS, ACCOUNT_CREDENTIALS], [None, SETTINGS]],
            [[ACCOUNT_CREDENTIALS, EMPTY_ACCOUNT_CREDENTIALS], [SETTINGS, None]],
        ],
    )
    def test_should_create_if_only_one_source_is_given(
        self,
        sources: list[dict | None],
        detected_settings: list[dict | None],
    ):
        detect_settings = mock.MagicMock(side_effect=detected_settings)
        retrieve = mock.sentinel.some_object
        detect_retriever = mock.MagicMock(return_value=retrieve)
        auth = mock.MagicMock()
        create_auth = mock.MagicMock(return_value=auth)
        session = mock.MagicMock()
        create_session = mock.MagicMock(return_value=session)
        result = client.create(
            credential_sources=sources,
            token_url=TOKEN_URL,
            detect_settings=detect_settings,
            detect_retriever=detect_retriever,
            create_auth=create_auth,
            create_session=create_session,
        )
        assert result.auth == auth
        assert result.session == session
        detect_settings.assert_has_calls([mock.call(source) for source in sources])
        detect_retriever.assert_called_with(SETTINGS)
        create_auth.assert_called_with(retrieve, config.TokenProviderSettings(token_url=TOKEN_URL))
        create_session.assert_called_with(auth)

    @pytest.mark.parametrize(
        "sources, settings, error",
        [
            [
                [ACCOUNT_CREDENTIALS, ACCOUNT_CREDENTIALS],
                SETTINGS,
                client.MultipleCredentialsSources,
            ],
            [
                [EMPTY_ACCOUNT_CREDENTIALS, EMPTY_ACCOUNT_CREDENTIALS],
                None,
                client.MissingCredentials,
            ],
        ],
    )
    def test_fails_to_create_if_multiple_or_no_sources_are_given(
        self, sources: list[dict | None], settings, error: type[ValueError]
    ):
        detect_settings = mock.MagicMock(return_value=settings)
        with pytest.raises(error):
            client.create(
                credential_sources=sources,
                token_url=TOKEN_URL,
                detect_settings=detect_settings,
                detect_retriever=self.unreachable,
                create_auth=self.unreachable,
                create_session=self.unreachable,
            )
        detect_settings.assert_has_calls([mock.call(source) for source in sources])
        self.unreachable.assert_not_called()


class TestCollectCredentials:
    def test_should_collect_credentials(self):
        config_credentials = {"some": "data"}
        read_config = mock.MagicMock(return_value=config_credentials)
        expected_sources = [
            config_credentials,
            {"username": constants.USER_EMAIL, "password": constants.PASSWORD},
        ]
        assert (
            client.collect_credentials(
                CONFIG_FILE,
                constants.USER_EMAIL,
                constants.PASSWORD,
                read_config,
            )
            == expected_sources
        )
