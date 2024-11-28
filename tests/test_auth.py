from typing import MutableMapping, Union, cast

import mock
import requests

from up42 import auth as up42_auth

from .fixtures import fixtures_globals as constants

CONFIG_FILE = "some-config-file"
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {constants.TOKEN}",
    "custom": "header",
}


class TestCollectCredentials:
    def test_should_collect_credentials(self):
        config_credentials = {"some": "data"}
        read_config = mock.MagicMock(return_value=config_credentials)
        expected_sources = [
            config_credentials,
            {"username": constants.USER_EMAIL, "password": constants.PASSWORD},
        ]
        assert (
            up42_auth.collect_credentials(
                CONFIG_FILE,
                constants.USER_EMAIL,
                constants.PASSWORD,
                read_config,
            )
            == expected_sources
        )


client = mock.MagicMock()
session = requests.Session()
session.headers = cast(MutableMapping[str, Union[str, bytes]], REQUEST_HEADERS)
client.session = session


class TestAuth:
    def setup_method(self, _):
        credential_sources = [{"some": "credentials"}]
        get_sources = mock.MagicMock(return_value=credential_sources)
        create_client = mock.MagicMock(return_value=client)

        self.auth = up42_auth.Auth(
            cfg_file=CONFIG_FILE,
            username=constants.USER_EMAIL,
            password=constants.PASSWORD,
            get_credential_sources=get_sources,
            create_client=create_client,
        )

        get_sources.assert_called_once_with(
            CONFIG_FILE,
            constants.USER_EMAIL,
            constants.PASSWORD,
        )
        create_client.assert_called_once_with(credential_sources, constants.TOKEN_ENDPOINT)
