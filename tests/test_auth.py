import json
import random
from typing import Dict, MutableMapping, Optional, Union, cast

import mock
import pytest
import requests
import requests_mock as req_mock

from up42 import auth as up42_auth

from . import helpers
from .fixtures import fixtures_globals as constants

CONFIG_FILE = "some-config-file"
URL = constants.API_HOST + "/some-url"
RESPONSE_TEXT = "some-response-text"
ERROR = {"some": "error"}
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {constants.TOKEN}",
    "custom": "header",
}


@pytest.fixture(name="http_method", params=["GET", "POST", "PUT", "DELETE", "HEAD"])
def _http_method(request):
    return request.param


@pytest.fixture(name="request_data", params=[{}, {"some": "data"}])
def _request_data(request):
    return request.param


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

    def test_should_authenticate_when_created(self):
        assert self.auth.session == session

    @pytest.mark.parametrize(
        "expected",
        [
            {"data": {"api-v1": "response"}, "error": {}},
            {"data": {"api-v1": "response"}},
            {"api-v2": "response"},
        ],
    )
    def test_should_pass_dict_for_json_response(
        self,
        http_method: str,
        request_data: dict,
        expected: dict,
        requests_mock: req_mock.Mocker,
    ):
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            json=expected,
            additional_matcher=helpers.match_request_body(request_data),
        )
        assert self.auth.request(http_method, URL, request_data) == expected

    def test_should_pass_text_for_text_response(
        self, http_method: str, request_data: dict, requests_mock: req_mock.Mocker
    ):
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            text=RESPONSE_TEXT,
            additional_matcher=helpers.match_request_body(request_data),
        )
        assert self.auth.request(http_method, URL, request_data) == RESPONSE_TEXT

    def test_should_pass_response(self, http_method: str, request_data: dict, requests_mock: req_mock.Mocker):
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            text=RESPONSE_TEXT,
            additional_matcher=helpers.match_request_body(request_data),
        )
        response = self.auth.request(http_method, URL, request_data, return_text=False)
        assert isinstance(response, requests.Response)
        assert response.text == RESPONSE_TEXT

    def test_fails_if_v1_api_request_fails(self, http_method: str, request_data: dict, requests_mock: req_mock.Mocker):
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            json={"error": ERROR},
            additional_matcher=helpers.match_request_body(request_data),
        )
        with pytest.raises(ValueError) as exc_info:
            self.auth.request(http_method, URL, request_data)

        assert str(exc_info.value) == str(ERROR)

    @pytest.mark.parametrize("return_text", [True, False])
    @pytest.mark.parametrize("error", [None, ERROR])
    def test_fails_if_status_code_is_bad(
        self,
        http_method: str,
        request_data: dict,
        return_text: bool,
        error: Optional[Dict],
        requests_mock: req_mock.Mocker,
    ):
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            status_code=random.randint(400, 599),
            json=error,
            additional_matcher=helpers.match_request_body(request_data),
        )
        with pytest.raises(requests.HTTPError) as exc_info:
            self.auth.request(http_method, URL, request_data, return_text=return_text)
        assert str(exc_info.value) == (json.dumps(error) if error else "")
