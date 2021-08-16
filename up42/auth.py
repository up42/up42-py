"""
UP42 authentication mechanism and base requests functionality
"""
import json
from pathlib import Path
from typing import Dict, Optional, Union

import requests
import requests.exceptions
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient, MissingTokenError
from tenacity import (
    Retrying,
    wait_fixed,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_exception,
    retry_if_exception_type,
    retry,
)

from up42.utils import get_logger

logger = get_logger(__name__)


class retry_if_429_error(retry_if_exception):
    """
    Altered tenacity retry strategy that retries if the exception is an ``HTTPError``
    with a 429 status code (too many requests).
    Adapted from https://github.com/alexwlchan/handling-http-429-with-tenacity
    """

    def __init__(self):
        def is_http_429_error(exception):
            return (
                isinstance(exception, requests.exceptions.HTTPError)
                and exception.response.status_code == 429
            )

        super().__init__(predicate=is_http_429_error)


class Auth:
    def __init__(
        self,
        cfg_file: Union[str, Path, None] = None,
        project_id: Optional[str] = None,
        project_api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        The Auth class handles the authentication with UP42.

        Info:
            Authentication is possible via the credentials of a specific project (project_id &
            project_api_key). To get your **project id** and **project api key**, follow
            the instructions in the docs authentication chapter.

        Args:
            cfg_file: File path to the cfg.json with {project_id: "...", project_api_key: "..."}.
            project_id: The unique identifier of the project.
            project_api_key: The project-specific API key.
        """
        self.cfg_file = cfg_file
        self.project_id = project_id
        self.project_api_key = project_api_key
        self.workspace_id: Optional[str] = None
        self.token: Optional[str] = None

        try:
            self.env: str = kwargs["env"]
        except KeyError:
            self.env = "com"
        try:
            self.authenticate: bool = kwargs["authenticate"]
        except KeyError:
            self.authenticate = True
        try:
            self.retry: bool = kwargs["retry"]
        except KeyError:
            self.retry = True

        if self.authenticate:
            self._find_credentials()
            self._get_token()
            self._get_workspace()
            logger.info("Authentication with UP42 successful!")

    def __repr__(self):
        return f"UP42ProjectAuth(project_id={self.project_id}, env={self.env})"

    def _find_credentials(self) -> None:
        """
        Sources the project credentials from a provided config file, error handling
        if no credentials are provided in arguments or config file.
        """
        if self.project_id is None or self.project_api_key is None:
            if self.cfg_file is None:
                raise ValueError(
                    "Provide project_id and project_api_key via arguments or config file!"
                )

            # Source credentials from config file.
            try:
                with open(self.cfg_file) as src:
                    config = json.load(src)
                    try:
                        self.project_id = config["project_id"]
                        self.project_api_key = config["project_api_key"]
                    except KeyError as e:
                        raise ValueError(
                            "Provided config file does not contain project_id and "
                            "project_api_key!"
                        ) from e
                logger.info("Got credentials from config file.")
            except FileNotFoundError as e:
                raise ValueError("Selected config file does not exist!") from e

        elif all(
            v is not None
            for v in [self.cfg_file, self.project_id, self.project_api_key]
        ):
            logger.info(
                "Credentials are provided via arguments and config file, "
                "now using the argument credentials."
            )

    def _endpoint(self) -> str:
        """Gets the endpoint."""
        return f"https://api.up42.{self.env}"

    def _get_token(self):
        """Project specific authentication via project id and project api key."""
        try:
            client = BackendApplicationClient(
                client_id=self.project_id, client_secret=self.project_api_key
            )
            auth = HTTPBasicAuth(self.project_id, self.project_api_key)
            get_token_session = OAuth2Session(client=client)
            token_response = get_token_session.fetch_token(
                token_url=self._endpoint() + "/oauth/token", auth=auth
            )
        except MissingTokenError as err:
            raise ValueError(
                "Authentication was not successful, check the provided project credentials."
            ) from err

        self.token = token_response["data"]["accessToken"]

    def _get_workspace(self) -> None:
        """Get workspace id belonging to authenticated project."""
        url = f"https://api.up42.{self.env}/projects/{self.project_id}"
        resp = self._request("GET", url)
        self.workspace_id = resp["data"]["workspaceId"]  # type: ignore

    @staticmethod
    def _generate_headers(token: str) -> Dict[str, str]:
        version = (
            Path(__file__)
            .resolve()
            .parent.joinpath("_version.txt")
            .read_text(encoding="utf-8")
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "cache-control": "no-cache",
            "X-UP42-info": f"python/{version}",
        }
        return headers

    # pylint: disable=dangerous-default-value
    @retry(
        retry=retry_if_429_error(),
        wait=wait_random_exponential(multiplier=0.5, max=180),
        reraise=True,
    )
    def _request_helper(
        self, request_type: str, url: str, data: dict = {}, querystring: dict = {}
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
        headers = self._generate_headers(self.token)  # type: ignore
        if querystring == {}:
            response = requests.request(
                method=request_type, url=url, data=json.dumps(data), headers=headers
            )
        else:
            response = requests.request(
                method=request_type,
                url=url,
                data=json.dumps(data),
                headers=headers,
                params=querystring,
            )
        logger.debug(response)
        logger.debug(data)
        response.raise_for_status()
        return response

    def _request(
        self,
        request_type: str,
        url: str,
        data: Union[dict, list] = {},
        querystring: dict = {},
        return_text: bool = True,
    ):  # Union[str, dict, requests.Response]:
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
        try:
            if self.retry:
                retryer = Retrying(
                    stop=stop_after_attempt(2),
                    wait=wait_fixed(0.5),
                    retry=(
                        retry_if_exception_type(requests.exceptions.HTTPError)
                        | retry_if_exception_type(requests.exceptions.ConnectionError)
                    ),
                    after=self._get_token(),
                    reraise=True,
                )
                response = retryer(
                    self._request_helper, request_type, url, data, querystring
                )
            else:
                response = self._request_helper(request_type, url, data, querystring)  # type: ignore
        except requests.exceptions.RequestException as err:  # Base error class
            err_message = json.loads(err.response.text)["error"]
            if "code" in err_message:
                err_message = f"{err_message['code']} Error - {err_message['message']}!"
            logger.error(err_message)
            raise requests.exceptions.RequestException(err_message) from err

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
