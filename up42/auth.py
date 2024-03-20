"""
UP42 authentication mechanism and base requests functionality
"""
import json
import pathlib
from typing import Dict, Optional, Union

import requests

from up42 import host, utils
from up42.http import client

logger = utils.get_logger(__name__)


def collect_credentials(
    cfg_file: Union[str, pathlib.Path, None],
    project_id: Optional[str],
    project_api_key: Optional[str],
    username: Optional[str],
    password: Optional[str],
):
    config_source = utils.read_json(cfg_file)
    project_credentials_source = {"project_id": project_id, "project_api_key": project_api_key}
    account_credentials_source = {"username": username, "password": password}
    return [config_source, project_credentials_source, account_credentials_source]


class Auth:
    def __init__(
        self,
        cfg_file: Union[str, pathlib.Path, None] = None,
        project_id: Optional[str] = None,
        project_api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        create_client=client.create,
        **kwargs,
    ):
        """
        The Auth class handles the authentication with UP42.

        Authenticate with UP42:
            https://sdk.up42.com/authentication/.

        Args:
            cfg_file: File path to the cfg.json with either
            {project_id: "...", project_api_key: "..."} or {username: "...", password: "..."}.
            project_id: The unique identifier of the project.
            project_api_key: The project-specific API key.
            username: The username for the UP42 account (email UP42 console).
            password: Password for the UP42 console login.
        """
        self.cfg_file = cfg_file
        self.workspace_id: Optional[str] = None
        authenticate: bool = kwargs.get("authenticate", True)

        if project_id:
            self.project_id = project_id

        self._client: Optional[client.Client] = None

        if authenticate:
            credential_sources = collect_credentials(cfg_file, project_id, project_api_key, username, password)
            self._client = create_client(credential_sources, host.endpoint("/oauth/token"))
            self._get_workspace()
            logger.info("Authentication with UP42 successful!")

    @property
    def token(self) -> Optional[str]:
        if self._client:
            return self._client.token
        return None

    def _get_workspace(self) -> None:
        """Get user id belonging to authenticated account."""
        url = host.endpoint("/users/me")
        resp = self.request("GET", url)
        self.workspace_id = resp["data"]["id"]

    def _generate_headers(self) -> Dict[str, str]:
        version = utils.get_up42_py_version()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "cache-control": "no-cache",
            "User-Agent": f"up42-py/{version} (https://github.com/up42/up42-py)",
        }
        return headers

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
        headers = self._generate_headers()
        response: requests.Response = requests.request(
            method=request_type,
            url=url,
            data=json.dumps(data),
            headers=headers,
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
        return_text: bool = True,
    ):
        """
        Handles retrying the request and automatically retries and gets a new token if
        the old is invalid.

        Retry is enabled by default, can be set to False as kwargs of Auth.

        In addition to this retry mechanic, 429-errors (too many requests) are retried
        more extensively in _request_helper.

        Args:
            request_type: 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
            url: The url to request.
            data: The payload, e.g. dictionary with job parameters etc.
            return_text: If true returns response text/json, false returns response.
        Returns:
            The API response.
        """

        try:
            response: requests.Response = self._request_helper(request_type, url, data)
            # There are two UP42 API versions:
            # v1 endpoints give response format {"data": ..., "error": ...}   data e.g. dict or list.  error str or dict
            # or None (if no error).
            # v1 always gives response, the error is indicated by the error key.
            # v2 endpoints follows RFC 7807: {"title":..., "status": 404} Optional "detail" and "type" keys.
            # v2 either gives above positive response, or fails with httperror (then check error.json() for the above
            # fields)
            # Handle response text.
            if return_text:
                try:
                    # TODO: try to be replaced with "json" in content type
                    response_text: dict = json.loads(response.text)
                    # Handle api error messages here before handling it in every single function.
                    if response_text.get("error", None) is not None and response_text.get("data", None) is None:
                        raise ValueError(response_text["error"])
                    # Catalog search, JobTask logs etc. does not have the usual {"data": {}, "error": {}} format.
                    return response_text
                except json.JSONDecodeError:  # e.g. JobTask logs are str format.
                    return response.text

            else:  # E.g. for DELETE
                return response

        except requests.exceptions.HTTPError as err:  # Base error class
            # Raising the original `err` error would not surface the relevant error message (contained in API response)
            err_message = err.response is not None and err.response.json()
            logger.error("Error %s", err_message)
            raise requests.exceptions.HTTPError(err_message) from err
