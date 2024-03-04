import base64
import dataclasses as dc
import time

from requests_mock import Mocker

from up42.http.config import ProjectCredentialsSettings, TokenProviderSettings
from up42.http.oauth import ProjectAuth

token_url = "https://localhost/oauth/token"
project_credentials = ProjectCredentialsSettings(
    client_id="client_id",
    client_secret="client_secret",
)

token_settings = TokenProviderSettings(
    token_url=token_url,
    duration=2,
    timeout=1,
)


def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode("utf-8"))
    return f'Basic {token.decode("ascii")}'


basic_client_auth = basic_auth(project_credentials.client_id, project_credentials.client_secret)
basic_auth_headers = {"Authorization": basic_client_auth}


@dc.dataclass
class FakeRequest:
    headers: dict


fake_request = FakeRequest(headers={})


def create_project_auth():
    return ProjectAuth(
        supply_credentials_settings=lambda: project_credentials,
        supply_token_settings=lambda: token_settings,
    )


class TestProjectAuth:
    def test_should_fetch_token_when_created(self, requests_mock: Mocker):
        token_value = "some-value"
        requests_mock.post(token_url, json={"access_token": token_value}, request_headers=basic_auth_headers)
        project_auth = create_project_auth()
        project_auth(fake_request)
        assert fake_request.headers["Authorization"] == f"Bearer {token_value}"
        assert project_auth.token.access_token == token_value
        assert requests_mock.called_once

    def test_should_fetch_token_when_expired(self, requests_mock: Mocker):
        responses = [{"json": {"access_token": f"token{idx}"}} for idx in range(1, 3)]
        requests_mock.post(token_url, response_list=responses, request_headers=basic_auth_headers)
        project_auth = create_project_auth()
        time.sleep(token_settings.duration + 1)
        project_auth(fake_request)
        expected_token_value = "token2"
        assert fake_request.headers["Authorization"] == f"Bearer {expected_token_value}"
        assert project_auth.token.access_token == expected_token_value
        assert requests_mock.call_count == 2
