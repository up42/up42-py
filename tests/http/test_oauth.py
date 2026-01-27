import copy
import dataclasses
import datetime
import random
import time
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42.http import config, oauth

HTTP_TIMEOUT = 10
TOKEN_VALUE = "some-token"
TOKEN_URL = "https://localhost/oauth/token"
TOKEN_EXPIRES_IN = 3
ACCOUNT_CREDENTIALS = config.AccountCredentialsSettings(username="some-user", password="some-pass")
TOKEN_SETTINGS = config.TokenProviderSettings(token_url=TOKEN_URL, timeout=HTTP_TIMEOUT, expiry_offset=1)


@pytest.fixture
def freeze_time():
    now = datetime.datetime.now()
    with mock.patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        yield


@pytest.fixture(name="token")
def _token():
    return oauth.Token(
        access_token=TOKEN_VALUE,
        expires_on=datetime.datetime.now()
        + datetime.timedelta(seconds=TOKEN_EXPIRES_IN - TOKEN_SETTINGS.expiry_offset),
    )


def match_account_authentication_request_body(request):
    return request.text == (
        "grant_type=password&"
        f"username={ACCOUNT_CREDENTIALS.username}&"
        f"password={ACCOUNT_CREDENTIALS.password}&"
        f"client_id={oauth.CLIENT_ID}&"
        "scope=openid"
    )


class TestAccountTokenRetriever:
    @pytest.mark.usefixtures("freeze_time")
    def test_should_retrieve(self, requests_mock: req_mock.Mocker, token):
        retrieve = oauth.AccountTokenRetriever(ACCOUNT_CREDENTIALS)
        requests_mock.post(
            TOKEN_URL,
            json={"access_token": TOKEN_VALUE, "expires_in": TOKEN_EXPIRES_IN},
            request_headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            additional_matcher=match_account_authentication_request_body,
        )
        assert retrieve(requests.Session(), TOKEN_SETTINGS) == token
        assert requests_mock.called_once

    def test_fails_to_retrieve_for_bad_response(self, requests_mock: req_mock.Mocker):
        retrieve = oauth.AccountTokenRetriever(ACCOUNT_CREDENTIALS)
        requests_mock.post(
            TOKEN_URL,
            status_code=random.randint(400, 599),
            request_headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            additional_matcher=match_account_authentication_request_body,
        )
        with pytest.raises(oauth.WrongCredentials):
            retrieve(requests.Session(), TOKEN_SETTINGS)
        assert requests_mock.called_once


mock_request = mock.MagicMock()
mock_request.headers = {}


class TestUp42Auth:
    def test_should_fetch_token_when_created(self, token):
        retrieve = mock.MagicMock(return_value=token)
        up42_auth = oauth.Up42Auth(retrieve=retrieve, token_settings=TOKEN_SETTINGS)
        up42_auth(mock_request)
        assert mock_request.headers["Authorization"] == f"Bearer {TOKEN_VALUE}"
        retrieve.assert_called_once()
        assert TOKEN_SETTINGS == retrieve.call_args.args[1]

    def test_should_fetch_token_when_expired(self, token):
        second_token = oauth.Token(access_token="token2", expires_on=datetime.datetime.max)
        retrieve = mock.MagicMock(side_effect=[token, second_token])
        up42_auth = oauth.Up42Auth(retrieve=retrieve, token_settings=TOKEN_SETTINGS)
        time.sleep(TOKEN_EXPIRES_IN)
        up42_auth(mock_request)

        assert mock_request.headers["Authorization"] == f"Bearer {second_token.access_token}"
        assert TOKEN_SETTINGS == retrieve.call_args.args[1]
        assert retrieve.call_count == 2

    def test_should_deepcopy_itself(self, token):
        retrieve = mock.MagicMock(return_value=token)
        up42_auth = oauth.Up42Auth(retrieve=retrieve, token_settings=TOKEN_SETTINGS)
        assert copy.deepcopy(up42_auth) == up42_auth
        retrieve.assert_called_once()


class TestDetectSettings:
    def test_should_detect_account_credentials(self):
        assert oauth.detect_settings(dataclasses.asdict(ACCOUNT_CREDENTIALS)) == ACCOUNT_CREDENTIALS

    def test_should_accept_empty_credentials(self):
        credentials = {"username": None, "password": None}
        assert not oauth.detect_settings(credentials)

    def test_should_accept_missing_credentials(self):
        assert not oauth.detect_settings(None)

    def test_fails_if_credentials_are_incomplete(self):
        credentials = {"key1": "value1", "key2": None}
        with pytest.raises(oauth.IncompleteCredentials):
            oauth.detect_settings(credentials)

    def test_fails_if_credentials_are_invalid(self):
        credentials = {"key1": "value1", "key2": "value2"}
        with pytest.raises(oauth.InvalidCredentials):
            oauth.detect_settings(credentials)


class TestDetectRetriever:
    def test_should_detect_account_retriever(self):
        assert isinstance(oauth.detect_retriever(ACCOUNT_CREDENTIALS), oauth.AccountTokenRetriever)

    def test_fails_if_settings_are_not_recognized(self):
        credentials = mock.MagicMock()
        with pytest.raises(oauth.UnsupportedSettings) as exc_info:
            oauth.detect_retriever(credentials)
        assert str(credentials) in str(exc_info.value)
