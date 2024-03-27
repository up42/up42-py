import json
import random
from typing import Dict, Optional

import mock
import pytest
import requests
import requests_mock as req_mock

from up42 import auth as up42_auth

from .fixtures import fixtures_globals as constants

SDK_VERSION = "some-version"
USER_NAME = "some-username"
PASSWORD = "some-password"
CONFIG_FILE = "some-config-file"
TOKEN_ENDPOINT = constants.API_HOST + "/oauth/token"
WORKSPACE_ENDPOINT = constants.API_HOST + "/users/me"
URL = constants.API_HOST + "/some-url"
RESPONSE_TEXT = "some-response-text"
ERROR = {"some": "error"}
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {constants.TOKEN}",
    "cache-control": "no-cache",
    "User-Agent": f"up42-py/{SDK_VERSION} ({up42_auth.REPOSITORY_URL})",
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
            {
                "project_id": constants.PROJECT_ID,
                "project_api_key": constants.PROJECT_APIKEY,
            },
            {"username": USER_NAME, "password": PASSWORD},
        ]
        assert (
            up42_auth.collect_credentials(
                CONFIG_FILE,
                constants.PROJECT_ID,
                constants.PROJECT_APIKEY,
                USER_NAME,
                PASSWORD,
                read_config,
            )
            == expected_sources
        )


def create_auth(requests_mock: req_mock.Mocker):
    credential_sources = [{"some": "credentials"}]
    get_sources = mock.MagicMock(return_value=credential_sources)
    create_client = mock.MagicMock()
    create_client.return_value.token = constants.TOKEN
    requests_mock.get(
        WORKSPACE_ENDPOINT,
        json={"data": {"id": constants.WORKSPACE_ID}},
    )
    auth = up42_auth.Auth(
        cfg_file=CONFIG_FILE,
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
        username=USER_NAME,
        password=PASSWORD,
        get_credential_sources=get_sources,
        create_client=create_client,
        version=SDK_VERSION,
    )

    get_sources.assert_called_once_with(
        CONFIG_FILE,
        constants.PROJECT_ID,
        constants.PROJECT_APIKEY,
        USER_NAME,
        PASSWORD,
    )
    create_client.assert_called_once_with(credential_sources, TOKEN_ENDPOINT)
    return auth


class TestAuth:
    def test_should_not_authenticate_if_requested(self):
        unreachable = mock.MagicMock()
        auth = up42_auth.Auth(
            cfg_file=CONFIG_FILE,
            project_id=constants.PROJECT_ID,
            project_api_key=constants.PROJECT_APIKEY,
            username=USER_NAME,
            password=PASSWORD,
            authenticate=False,
            get_sources=unreachable,
            create_client=unreachable,
            version=SDK_VERSION,
        )
        assert auth.project_id == constants.PROJECT_ID
        assert not auth.workspace_id
        assert not auth.token
        unreachable.assert_not_called()

    def test_should_authenticate_when_created(self, requests_mock: req_mock.Mocker):
        auth = create_auth(requests_mock)
        assert auth.project_id == constants.PROJECT_ID
        assert auth.workspace_id == constants.WORKSPACE_ID
        assert auth.token == constants.TOKEN

    @pytest.mark.parametrize(
        "expected",
        [
            {"data": {"api-v1": "response"}, "error": {}},
            {"data": {"api-v1": "response"}},
            {"api-v2": "response"},
        ],
    )
    def test_should_respond_with_dict_for_json_response(
        self,
        http_method: str,
        request_data: dict,
        expected: dict,
        requests_mock: req_mock.Mocker,
    ):
        auth = create_auth(requests_mock)
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            json=expected,
        )
        assert auth.request(http_method, URL, request_data) == expected

    def test_should_respond_with_text_for_text_response(
        self, http_method: str, request_data: dict, requests_mock: req_mock.Mocker
    ):
        auth = create_auth(requests_mock)
        requests_mock.request(http_method, URL, request_headers=REQUEST_HEADERS, text=RESPONSE_TEXT)
        assert auth.request(http_method, URL, request_data) == RESPONSE_TEXT

    def test_should_pass_response(self, http_method: str, request_data: dict, requests_mock: req_mock.Mocker):
        auth = create_auth(requests_mock)
        requests_mock.request(http_method, URL, request_headers=REQUEST_HEADERS, text=RESPONSE_TEXT)
        response = auth.request(http_method, URL, request_data, return_text=False)
        assert isinstance(response, requests.Response)
        assert response.text == RESPONSE_TEXT

    def test_should_fail_if_v1_api_request_fails(
        self, http_method: str, request_data: dict, requests_mock: req_mock.Mocker
    ):
        auth = create_auth(requests_mock)

        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            json={"error": ERROR},
        )
        with pytest.raises(ValueError) as exc_info:
            auth.request(http_method, URL, request_data)

        assert str(exc_info.value) == str(ERROR)

    @pytest.mark.parametrize("return_text", [True, False])
    @pytest.mark.parametrize("error", [None, ERROR])
    def test_should_fail_for_bad_status_code(
        self,
        http_method: str,
        request_data: dict,
        return_text: bool,
        error: Optional[Dict],
        requests_mock: req_mock.Mocker,
    ):
        auth = create_auth(requests_mock)
        requests_mock.request(
            http_method,
            URL,
            request_headers=REQUEST_HEADERS,
            status_code=random.randint(400, 599),
            json=error,
        )
        with pytest.raises(requests.HTTPError) as exc_info:
            auth.request(http_method, URL, request_data, return_text=return_text)
        assert str(exc_info.value) == (json.dumps(error) if error else "")
