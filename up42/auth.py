"""
UP42 authentication mechanism and base requests functionality
"""
import json
import pathlib
import warnings
from typing import Dict, Optional, Union, cast

import requests
import requests_oauthlib as roauthlib  # type:ignore
import tenacity as tnc
from oauthlib import oauth2

from up42 import host, utils

logger = utils.get_logger(__name__)


def retry_for_error_status_code(code: int):
    class StatusCodeRetry(tnc.retry_if_exception):
        def __init__(self):
            def is_http_error(exception):
                return (
                    isinstance(exception, requests.exceptions.HTTPError)
                    and exception.response is not None
                    and exception.response.status_code == code
                )

            super().__init__(predicate=is_http_error)

    return StatusCodeRetry()


class Auth:
    def __init__(
        self,
        cfg_file: Union[str, pathlib.Path, None] = None,
        project_id: Optional[str] = None,
        project_api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
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
        self.token: Optional[str] = None

        credentials_dict = {
            "project_id": project_id,
            "project_api_key": project_api_key,
            "username": username,
            "password": password,
        }
        credentials_dict = {key: value for key, value in credentials_dict.items() if value}

        self.authenticate: bool = kwargs.get("authenticate", True)

        if project_id:
            self.project_id = project_id

        config = self._choose_credential_source(cfg_file, credentials_dict)

        if self.authenticate:
            self._set_credentials(source=config)
            self._get_token()
            self._get_workspace()
            logger.info("Authentication with UP42 successful!")

    def _choose_credential_source(self, cfg_file: Union[str, pathlib.Path, None], kwargs: dict) -> dict:
        config = utils.read_json(cfg_file) or {}
        if set(config.keys()).intersection(set(kwargs.keys())):
            raise ValueError("Credentials must be provided either via config file or arguments, but not both")
        return config if config else kwargs

    def _set_credentials(self, source: dict):
        schemas = {
            "user": ("username", "password"),
            "project": ("project_id", "project_api_key"),
        }
        token_retrievers = {
            "user": self._get_token_account_based,
            "project": self._get_token_project_based,
        }

        self._credentials_id = None

        for schema, parameters in schemas.items():
            if set(parameters).issubset(source.keys()):
                if schema == "project":
                    warnings.warn(
                        "Project based authentication will be deprecated."
                        "Please follow authentication guidelines (/docs/authentication.md)."
                    )
                self._credentials_id = source[parameters[0]]
                self._credentials_key = source[parameters[1]]
                self._get_token = token_retrievers[schema]
        if self._credentials_id is None:
            raise ValueError("No credentials provided either via config file or arguments.")

    def _get_token_account_based(self):
        """Account based authentication via username and password."""
        try:
            req_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            req_body = {
                "grant_type": "password",
                "username": self._credentials_id,
                "password": self._credentials_key,
            }
            token_response = requests.post(
                url=host.endpoint("/oauth/token"),
                data=req_body,
                headers=req_headers,
                timeout=120,
            )
            if token_response.status_code != 200:
                raise ValueError(
                    f"Authentication failed with status code {token_response.status_code}."
                    "Check the provided credentials."
                )
        except requests.exceptions.RequestException as err:
            raise ValueError(
                "Authentication failed due to a network error. Check the provided credentials and network connectivity."
            ) from err
        self.token = token_response.json()["data"]["accessToken"]

    def _get_token_project_based(self):
        """Project specific authentication via project id and project api key."""
        try:
            client_id = cast(str, self._credentials_id)
            client_secret = cast(str, self._credentials_key)
            client = oauth2.BackendApplicationClient(client_id=client_id, client_secret=client_secret)
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            get_token_session = roauthlib.OAuth2Session(client=client)
            token_response = get_token_session.fetch_token(token_url=host.endpoint("/oauth/token"), auth=auth)
        except oauth2.MissingTokenError as err:
            raise ValueError("Authentication was not successful, check the provided project credentials.") from err

        self.token = token_response["data"]["accessToken"]

    def _get_workspace(self) -> None:
        """Get user id belonging to authenticated account."""
        url = host.endpoint("/users/me")
        resp = self.request("GET", url)
        self.workspace_id = resp["data"]["id"]

    @staticmethod
    def _generate_headers(token: Optional[str]) -> Dict[str, str]:
        version = utils.get_up42_py_version()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "cache-control": "no-cache",
            "User-Agent": f"up42-py/{version} (https://github.com/up42/up42-py)",
        }
        return headers

    # pylint: disable=dangerous-default-value
    @tnc.retry(
        retry=retry_for_error_status_code(429),
        wait=tnc.wait_random_exponential(multiplier=0.5, max=180),
        reraise=True,
    )
    def _request_helper(
        self,
        request_type: str,
        url: str,
        data: dict = {},
        querystring: dict = {},
    ) -> requests.Response:
        """
        Helper function for the request, running the actual request with the correct headers.

        Args:
            request_type: 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
            url: The requests url.
            data: The payload, e.g. dictionary with job parameters etc.
            querystring: The querystring.

        Returns:
            The request response.
        """
        headers = self._generate_headers(self.token)
        if querystring == {}:
            response: requests.Response = requests.request(
                method=request_type,
                url=url,
                data=json.dumps(data),
                headers=headers,
                timeout=120,
            )
        else:
            response = requests.request(
                method=request_type,
                url=url,
                data=json.dumps(data),
                headers=headers,
                params=querystring,
                timeout=120,
            )
        logger.debug(response)
        logger.debug(data)
        response.raise_for_status()
        return response

    def request(
        self,
        request_type: str,
        url: str,
        data: Union[dict, list] = {},
        querystring: dict = {},
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
            querystring: The querystring.
            return_text: If true returns response text/json, false returns response.
            retry: If False, after 5 minutes and invalid token will return 401
                errors.

        Returns:
            The API response.
        """
        retryer_token = tnc.Retrying(
            stop=tnc.stop_after_attempt(2),  # Original attempt + one retry
            wait=tnc.wait_fixed(0.5),
            retry=(retry_for_error_status_code(401) | tnc.retry_if_exception_type(requests.exceptions.ConnectionError)),
            after=lambda retry_state: self._get_token(),  # type:ignore
            reraise=True,
            # after final failed attempt, raises last attempt's exception instead of RetryError.
        )

        try:
            response: requests.Response = retryer_token(self._request_helper, request_type, url, data, querystring)

        # There are two UP42 API versions:
        # v1 endpoints give response format {"data": ..., "error": ...}   data e.g. dict or list.  error str or dict
        # or None (if no error).
        # v1 always gives response, the error is indicated by the error key.
        # v2 endpoints follows RFC 7807: {"title":..., "status": 404} Optional "detail" and "type" keys.
        # v2 either gives above positive response, or fails with httperror (then check error.json() for the above
        # fields)

        except requests.exceptions.HTTPError as err:  # Base error class
            # Raising the original `err` error would not surface the relevant error message (contained in API response)
            err_message = err.response is not None and err.response.json()
            logger.error("Error %s", err_message)
            raise requests.exceptions.HTTPError(err_message) from err

        # Handle response text.
        if return_text:
            try:
                response_text = json.loads(response.text)
            except json.JSONDecodeError:  # e.g. JobTask logs are str format.
                response_text = response.text

            # Handle api error messages here before handling it in every single function.
            try:
                if response_text["error"] is not None and response_text["data"] is None:
                    raise ValueError(response_text["error"])
                return response_text
            except (
                KeyError,
                TypeError,
            ):  # Catalog search, JobTask logs etc. does not have the usual {"data":"",
                # "error":""} format.
                return response_text

        else:  # E.g. for DELETE
            return response
