import json
from pathlib import Path
from typing import Dict, List, Union

import requests
import requests.exceptions
import pandas as pd
from tenacity import (
    Retrying,
    RetryError,
    wait_fixed,
    stop_after_attempt,
    retry_if_exception_type,
)

from .tools import Tools
from .utils import get_logger

# TODO: Logger produces multiple printouts in Jupyter Lab, known issue.
logger = get_logger(__name__)  # level=logging.CRITICAL  #INFO

# TODO: Test stuff with nonlinear structure.


class Api(Tools):
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
        return f"UP42ProjectAPI(project_id={self.project_id}, env={self.env})"

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

    def initialize_project(self) -> "Project":
        """Directly returns the correct project object (has to exist on UP42)."""
        from .project import Project

        project = Project(api=self, project_id=self.project_id)
        return project

    def initialize_catalog(self, backend: str = "ONE_ATLAS") -> "Catalog":
        """Directly returns a catalog object."""
        from .catalog import Catalog

        return Catalog(api=self, backend=backend)

    def initialize_workflow(self, workflow_id) -> "Workflow":
        """Directly returns a workflow object (has to exist on UP42)."""
        from .workflow import Workflow

        workflow = Workflow(
            api=self, workflow_id=workflow_id, project_id=self.project_id
        )
        return workflow

    def initialize_job(self, job_id, order_ids: List[str] = [""]) -> "Job":
        """Directly returns a Job object (has to exist on UP42)."""
        from .job import Job

        job = Job(
            api=self, job_id=job_id, project_id=self.project_id, order_ids=order_ids
        )
        return job

    def initialize_jobtask(self, job_task_id, job_id) -> "JobTask":
        """Directly returns a JobTask object (has to exist on UP42)."""
        from .jobtask import JobTask

        jobtask = JobTask(
            api=self, job_task_id=job_task_id, job_id=job_id, project_id=self.project_id
        )
        return jobtask

    def get_blocks(
        self, block_type=None, basic: bool = True, as_dataframe=False,
    ) -> Union[Dict, List[Dict]]:
        """
        Gets a list of all public blocks on the marketplace.

        Args:
            block_type: Optionally filters to "data" or "processing" blocks, default None.
            basic: Optionally returns simple version {block_id : block_name}
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            A list of the public blocks and their metadata. Optional a simpler version
            dict.
        """
        try:
            block_type = block_type.lower()
        except AttributeError:
            pass

        url = f"{self._endpoint()}/blocks"
        response_json = self._request(request_type="GET", url=url)
        public_blocks_json = response_json["data"]

        if block_type == "data":
            logger.info("Getting only data blocks.")
            blocks_json = [
                block for block in public_blocks_json if block["type"] == "DATA"
            ]
        elif block_type == "processing":
            logger.info("Getting only processing blocks.")
            blocks_json = [
                block for block in public_blocks_json if block["type"] == "PROCESSING"
            ]
        else:
            blocks_json = public_blocks_json

        if basic:
            logger.info(
                "Getting basic information, use basic=False for all block details."
            )
            blocks_basic = {block["name"]: block["id"] for block in blocks_json}
            if as_dataframe:
                return pd.DataFrame.from_dict(blocks_basic, orient="index")
            else:
                return blocks_basic

        else:
            if as_dataframe:
                return pd.DataFrame(blocks_json)
            else:
                return blocks_json

    def get_block_details(self, block_id: str, as_dataframe=False) -> Dict:
        """
        Gets the detailed information about a specific (public or custom) block from
        the server, includes all manifest.json and marketplace.json contents.

        Args:
            block_id: The block id.
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            A dict of the block details metadata for the specific block.
        """
        try:
            url = f"{self._endpoint()}/blocks/{block_id}"  # public blocks
            response_json = self._request(request_type="GET", url=url)
        except (requests.exceptions.HTTPError, RetryError):
            url = f"{self._endpoint()}/users/me/blocks/{block_id}"  # custom blocks
            response_json = self._request(request_type="GET", url=url)
        details_json = response_json["data"]

        if as_dataframe:
            return pd.DataFrame.from_dict(details_json, orient="index").transpose()
        else:
            return details_json

    def get_environments(self, as_dataframe=False) -> Dict:
        """
        Gets all existing UP42 environments, used for separating storage of API keys
        etc.

        Args:
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            The environments as json info.
        """
        url = f"{self._endpoint()}/environments"
        response_json = self._request(request_type="GET", url=url)
        environments_json = response_json["data"]

        if as_dataframe:
            return pd.DataFrame(environments_json)
        else:
            return environments_json

    def create_environment(self, name: str, environment_variables: Dict = None) -> Dict:
        """
        Creates a new UP42 environments, used for separating storage of API keys
        etc.

        Args:
            name: Name of the new environment.
            environment_variables: The variables to add to the environment, see example.

        Returns:
            The json info of the newly created environment.

        Example:
            ```python
            environment_variables=
                {"username": "up42", "password": "password"}
            ```
        """
        existing_environment_names = [env["name"] for env in self.get_environments()]
        if name in existing_environment_names:
            raise Exception("An environment with the name %s already exists.", name)
        payload = {"name": name, "secrets": environment_variables}
        url = f"{self._endpoint()}/environments"
        response_json = self._request(request_type="POST", url=url, data=payload)
        return response_json["data"]

    def delete_environment(self, environment_id: str) -> None:
        """
        Deletes a specific environment.

        Args:
            environment_id: The id of the environment to delete. See also get_environments.
        """
        url = f"{self._endpoint()}/environments/{environment_id}"
        self._request(request_type="DELETE", url=url, return_text=False)
        logger.info("Successfully deleted environment: %s", environment_id)

    def validate_manifest(self, path_or_json: Union[str, Path, Dict]) -> Dict:
        """
        Validates the block manifest, input either manifest json string or filepath.

        Args:
            path_or_json: The input manifest, either filepath or json string, see example.

        Returns:
            A dictionary with the validation result and potential validation errors.

        Example:
            ```json
                {
                    "_up42_specification_version": 2,
                    "name": "sharpening",
                    "type": "processing",
                    "tags": [
                        "imagery",
                        "processing"
                    ],
                    "display_name": "Sharpening Filter",
                    "description": "This block enhances the sharpness of a raster image by applying an unsharp mask filter algorithm.",
                    "parameters": {
                        "strength": {"type": "string", "default": "medium"}
                    },
                    "machine": {
                        "type": "large"
                    },
                    "input_capabilities": {
                        "raster": {
                            "up42_standard": {
                                "format": "GTiff"
                            }
                        }
                    },
                    "output_capabilities": {
                        "raster": {
                            "up42_standard": {
                                "format": "GTiff",
                                "bands": ">",
                                "sensor": ">",
                                "resolution": ">",
                                "dtype": ">",
                                "processing_level": ">"
                            }
                        }
                    }
                }
            ```
        """
        if isinstance(path_or_json, (str, Path)):
            with open(path_or_json) as src:
                manifest_json = json.load(src)
        else:
            manifest_json = path_or_json
        url = f"{self._endpoint()}/validate-schema/block"
        response_json = self._request(request_type="POST", url=url, data=manifest_json)
        logger.info("The manifest is valid.")
        return response_json["data"]
