import base64
import time

import mock
import requests
import requests_mock as req_mock

from up42.http import config, oauth

HTTP_TIMEOUT = 10
TOKEN_VALUE = "some-token"
TOKEN_URL = "https://localhost/oauth/token"
project_credentials = config.ProjectCredentialsSettings(
    client_id="client_id",
    client_secret="client_secret",
)
account_credentials = config.AccountCredentialsSettings(username="some-user", password="some-pass")


def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode("utf-8"))  # noqa: E231
    return f'Basic {token.decode("ascii")}'


basic_client_auth = basic_auth(project_credentials.client_id, project_credentials.client_secret)
basic_auth_headers = {"Authorization": basic_client_auth}


class TestProjectTokenRetriever:
    def test_should_retrieve(self, requests_mock: req_mock.Mocker):
        def match_request_body(request):
            return request.text == "grant_type=client_credentials"

        retrieve = oauth.ProjectTokenRetriever(lambda: project_credentials)
        requests_mock.post(
            TOKEN_URL,
            json={"access_token": TOKEN_VALUE},
            request_headers=basic_auth_headers,
            additional_matcher=match_request_body,
        )
        assert retrieve(requests.Session(), TOKEN_URL, HTTP_TIMEOUT) == TOKEN_VALUE
        assert requests_mock.called_once


class TestAccountTokenRetriever:
    def test_should_retrieve(self, requests_mock: req_mock.Mocker):
        def match_request_body(request):
            return request.text == (
                "grant_type=password&"
                f"username={account_credentials.username}&"
                f"password={account_credentials.password}"
            )

        retrieve = oauth.AccountTokenRetriever(lambda: account_credentials)
        requests_mock.post(
            TOKEN_URL,
            json={"access_token": TOKEN_VALUE},
            request_headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            additional_matcher=match_request_body,
        )
        assert retrieve(requests.Session(), TOKEN_URL, HTTP_TIMEOUT) == TOKEN_VALUE
        assert requests_mock.called_once


mock_request = mock.MagicMock()
mock_request.headers = {}
token_settings = config.TokenProviderSettings(
    token_url=TOKEN_URL,
    duration=2,
    timeout=HTTP_TIMEOUT,
)


class TestUp42Auth:
    def test_should_fetch_token_when_created(self):
        retrieve = mock.MagicMock(return_value=TOKEN_VALUE)
        up42_auth = oauth.Up42Auth(retrieve=retrieve, supply_token_settings=lambda: token_settings)
        up42_auth(mock_request)
        assert mock_request.headers["Authorization"] == f"Bearer {TOKEN_VALUE}"
        assert up42_auth.token.access_token == TOKEN_VALUE
        retrieve.assert_called_once()
        assert TOKEN_URL, HTTP_TIMEOUT == retrieve.call_args.args[1:]

    def test_should_fetch_token_when_expired(self):
        second_token = "token2"
        retrieve = mock.MagicMock(side_effect=["token1", second_token])
        up42_auth = oauth.Up42Auth(retrieve=retrieve, supply_token_settings=lambda: token_settings)
        time.sleep(token_settings.duration + 1)
        up42_auth(mock_request)

        assert mock_request.headers["Authorization"] == f"Bearer {second_token}"
        assert up42_auth.token.access_token == second_token
        assert TOKEN_URL, HTTP_TIMEOUT == retrieve.call_args.args[1:]
        assert retrieve.call_count == 2
