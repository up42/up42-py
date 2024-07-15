"""
UP42 authentication mechanism and base requests functionality
"""

import json
import pathlib
from typing import Callable, Dict, List, Optional, Union

import requests

from up42 import host, utils
from up42.http import client

logger = utils.get_logger(__name__)
ConfigurationSource = Optional[Union[str, pathlib.Path]]
ConfigurationReader = Callable[[ConfigurationSource], Optional[Dict]]
CredentialsMerger = Callable[
    [ConfigurationSource, Optional[str], Optional[str]],
    List[Optional[Dict]],
]
ClientFactory = Callable[[List[Optional[Dict]], str], client.Client]


def collect_credentials(
    cfg_file: ConfigurationSource,
    username: Optional[str],
    password: Optional[str],
    read_config: ConfigurationReader = utils.read_json,
) -> List[Optional[Dict]]:
    config_source = read_config(cfg_file)
    account_credentials_source = {"username": username, "password": password}
    return [config_source, account_credentials_source]


class Auth:
    def __init__(
        self,
        cfg_file: Union[str, pathlib.Path, None] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        get_credential_sources: CredentialsMerger = collect_credentials,
        create_client: ClientFactory = client.create,
    ):
        """
        The Auth class handles the authentication with UP42.

        Authenticate with UP42:
            https://sdk.up42.com/authentication/.

        Args:
            cfg_file: File path to the cfg.json with {username: "...", password: "..."}.
            username: The username for the UP42 account (email UP42 console).
            password: Password for the UP42 console login.
        """
        credential_sources = get_credential_sources(cfg_file, username, password)
        self.client = create_client(credential_sources, host.token_endpoint())
        logger.info("Authentication with UP42 successful!")

    @property
    def session(self) -> requests.Session:
        return self.client.session

    # pylint: disable=dangerous-default-value
    def _request_helper(
        self,
        request_type: str,
        url: str,
        data: dict,
    ) -> requests.Response:
        """
        Helper function for the request, running the actual request with the correct headers.

        Args:
            request_type: 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
            url: The requests url.
            data: The payload, e.g. dictionary with job parameters etc.
        Returns:
            The request response.
        """
        response: requests.Response = self.session.request(
            method=request_type,
            url=url,
            json=data,
            timeout=utils.TIMEOUT,
        )
        logger.debug(response)
        logger.debug(data)
        response.raise_for_status()
        return response

    def request(
        self,
        request_type: str,
        url: str,
        data: dict = {},
    ):
        """
        Makes a request to the API, handles authentication and SDK headers

        Args:
            request_type: 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
            url: The url to request.
            data: The payload, e.g. dictionary with job parameters etc.
            return_text: If true returns response text/json, false returns response.
        Returns:
            The response object or payload.
        """

        try:
            response: requests.Response = self._request_helper(request_type, url, data)
            try:
                response_json = response.json()
                # v1 endpoints give response format {"data": ..., "error": ...}
                if isinstance(response_json, dict) and response_json.get("error") and response_json.get("data") is None:
                    raise ValueError(response_json["error"])
                # Catalog search, JobTask logs etc. does not have the usual {"data": {}, "error": {}} format.
                return response_json
            except json.JSONDecodeError:  # e.g. JobTask logs are str format.
                return response.text

        except requests.exceptions.HTTPError as err:
            # v2 endpoints follow RFC 7807 for errors and will fail with http error
            # The corresponding errors to be handled in caller
            err_message = err.response is not None and err.response.text
            raise requests.exceptions.HTTPError(err_message) from err
