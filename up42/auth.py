import json
from pathlib import Path
from typing import Dict, List, Union

import requests
import requests.exceptions
from tenacity import (
    Retrying,
    wait_fixed,
    stop_after_attempt,
    retry_if_exception_type,
)

from .tools import Tools
from .utils import get_logger

# TODO: Logger produces multiple printouts in Jupyter Lab, known issue.
logger = get_logger(__name__)  # level=logging.CRITICAL  #INFO

# TODO: Test stuff with nonlinear structure.


class Auth(Tools):
    def __init__(
        self,
        cfg_file: Union[str, Path] = None,
        project_id: str = None,
        project_api_key: str = None,
        **kwargs,
    ):
        """
        The Api class handles the authentication with UP42, can create projects, gives
        access to the blocks on the UP42 marketplace, handles environment settings and
        other generic UP42 functions.

        Info:
            Authentication is possible via the credentials of a specific project (project_id &
            project_api_key). To get your **project id** and **project api key**, follow
            the instructions in the docs installation chapter.

        Public methods:
            initialize_project, get_blocks, get_block_details, delete_custom_block,
            get_environments, create_environment, delete_environment, validate_manifest

        Args:
            cfg_file: File path to the cfg.json with {project_id: "...", project_api_key: "..."}.
            project_id: The unique identifier of the project.
            project_api_key: The project-specific API key.
        """
        self.cfg_file = cfg_file
        self.project_id = project_id
        self.project_api_key = project_api_key

        self.env = "com"
        self.authenticate = True
        self.retry = True

        if kwargs is not None:
            try:
                self.env: str = kwargs["env"]
            except KeyError:
                pass
            try:
                self.authenticate: bool = kwargs["authenticate"]
            except KeyError:
                pass
            try:
                self.retry: bool = kwargs["retry"]
            except KeyError:
                pass

        if self.authenticate:
            self._find_credentials()
            self._get_token()
            logger.info("Authentication with UP42 successful!")

    def __repr__(self):
        return f"UP42ProjectAuth(project_id={self.project_id}, env={self.env})"

    def _find_credentials(self) -> None:
        """
        Finds the project credentials provided as class arguments or in the config file.
        """
        if self.cfg_file is None:
            if self.project_id is None or self.project_api_key is None:
                raise ValueError(
                    "Provide project credentials via arguments or config file!"
                )
        # Source credentials from config file.
        elif self.cfg_file is not None:
            try:
                with open(self.cfg_file) as src:
                    config = json.load(src)
                    try:
                        self.project_id = config["project_id"]
                        self.project_api_key = config["project_api_key"]
                    except KeyError:
                        raise ValueError(
                            "Provided config file does not conatin project_id and project_api_key!"
                        )
                logger.info("Got credentials from config.json.")
            except FileNotFoundError:
                raise ValueError("Selected config.json file does not exist!")
        else:
            raise ValueError(
                "Provide project credentials via arguments or config file!"
            )

    def _endpoint(self) -> str:
        """Gets the endpoint."""
        return f"https://api.up42.{self.env}"

    def _get_token(self) -> None:
        try:
            self._get_token_project()
        except requests.exceptions.HTTPError:
            raise ValueError(
                "Authentication was not successful, check the provided project keys."
            )

    def _get_token_project(self) -> None:
        """Project specific authentication via project id and project api key."""
        url = (
            f"https://{self.project_id}:{self.project_api_key}@api.up42.{self.env}"
            f"/oauth/token"
        )
        payload = "grant_type=client_credentials"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }
        token_response = requests.request("POST", url, data=payload, headers=headers)
        token_response.raise_for_status()
        token = json.loads(token_response.text)
        self.token = token["data"][
            "accessToken"
        ]  # pylint: disable=attribute-defined-outside-init

    @staticmethod
    def _generate_headers(token: str) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "cache-control": "no-cache",
        }
        return headers

    # pylint: disable=dangerous-default-value
    def _request_helper(
        self, request_type: str, url: str, data: Dict = {}, querystring: Dict = {}
    ) -> str:
        """
        Helper function for the request running the actual request with the correct headers.

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
        return response

    def _request(
        self,
        request_type: str,
        url: str,
        data: Union[Dict, List] = {},
        querystring: Dict = {},
        return_text: bool = True,
    ):
        """
        Handles retrying the request and automatically gets a new token if the old
        is invalid.

        Retry is enabled by default, can be set to False as kwargs in Api().

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
        if self.retry:
            retryer = Retrying(
                stop=stop_after_attempt(1),  # TODO: Find optimal retry solution
                wait=wait_fixed(0),
                retry=(
                    retry_if_exception_type(requests.exceptions.HTTPError)
                    | retry_if_exception_type(requests.exceptions.ConnectionError)
                ),
                after=self._get_token(),
            )
            response = retryer(
                self._request_helper, request_type, url, data, querystring
            )
        else:
            response = self._request_helper(request_type, url, data, querystring)

        # TODO: Improve error messages on backend.
        # TODO: Put error messages in the specific functions.
        if response.status_code != 200:
            if response.status_code == 403:
                raise ValueError(
                    "Access not possible, check if the given ids are correct, "
                    "you have sufficient credits, "
                    "that the referenced workflow/job object exists, "
                    "and if the aoi is too big (>1000 sqkm)."
                )
            elif response.status_code == 404:
                raise ValueError("Product not found!")

        # Handle response text.
        # TODO: Uniform error format on backend, too many different cases.
        if return_text:
            try:
                response_text = json.loads(response.text)
            except json.JSONDecodeError:  # e.g. JobTask logs are str format.
                response_text = response.text

            # Handle api error messages here before handling it in every single function.
            try:
                if response_text["error"] is not None and response_text["data"] is None:
                    raise ValueError(response_text["error"])
                else:
                    return response_text
            except (
                KeyError,
                TypeError,
            ):  # Catalog search, JobTask logs etc. does not have the usual {"data":"",
                # "error":""} format.
                return response_text

        else:  # E.g. for DELETE
            return response
