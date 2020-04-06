import logging
from typing import Dict, List, Union

from tqdm import tqdm

from .auth import Auth
from .tools import Tools
from .utils import get_logger
from .workflow import Workflow

logger = get_logger(__name__)


class Project(Tools):
    def __init__(self, auth: Auth, project_id: str):
        """
        The Project class can query all available workflows and spawn new workflows
        within an UP42 project. Also handles project user settings.

        Public Methods:
            create_workflow, get_workflows, get_project_settings,
            update_project_settings
        """
        self.auth = auth
        self.project_id = project_id
        if self.auth.get_info:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"Project(project_id={self.project_id}, auth={self.auth}, info={self.info})"
        )

    def _get_info(self):
        """Gets metadata info from sever for an existing project"""
        url = f"{self.auth._endpoint()}/projects/{self.project_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self.info = response_json["data"]
        return self.info

    def create_workflow(
        self, name: str, description: str = "", use_existing: bool = False
    ) -> "Workflow":
        """
        Creates a new workflow and returns a workflow object.

        Args:
            name: Name of the new workflow.
            description: Description of the new workflow.
            use_existing: If True, instead of creating a new workflow, uses the
                most recent workflow with the same name & description.

        Returns:
            The workflow object.
        """
        if use_existing:
            logger.info("Getting existing workflows in project ...")
            logging.getLogger("up42.workflow").setLevel(logging.CRITICAL)
            existing_workflows = self.get_workflows()
            logging.getLogger("up42.workflow").setLevel(logging.INFO)

            matching_workflows = [
                workflow
                for workflow in existing_workflows
                if workflow.info["name"] == name
                and workflow.info["description"] == description
            ]
            if matching_workflows:
                existing_workflow = matching_workflows[0]
                logger.info(
                    "Using existing workflow: %s, %s.",
                    name,
                    existing_workflow.workflow_id,
                )
                return existing_workflow

        url = f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
        payload = {"name": name, "description": description}
        response_json = self.auth._request(request_type="POST", url=url, data=payload)
        workflow_id = response_json["data"]["id"]
        logger.info("Created new workflow: %s.", workflow_id)
        workflow = Workflow(
            self.auth, project_id=self.project_id, workflow_id=workflow_id
        )
        return workflow

    def get_workflows(self, return_json: bool = False) -> Union[List["Workflow"], Dict]:
        """
        Gets all workflows in a project as workflow objects or json.

        Args:
            return_json: True returns Workflow Objects.

        Returns:
            Workflow objects in the project or alternatively json info of the workflows.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/workflows"
        response_json = self.auth._request(request_type="GET", url=url)
        workflows_json = response_json["data"]
        logger.info(
            "Got %s workflows for project %s.", len(workflows_json), self.project_id
        )

        if return_json:
            return workflows_json
        else:
            workflows = [
                Workflow(self.auth, project_id=self.project_id, workflow_id=work["id"])
                for work in tqdm(workflows_json)
            ]
            return workflows

    def get_project_settings(self) -> List:
        """
        Gets the project settings.

        Returns:
            The project settings.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/settings"
        response_json = self.auth._request(request_type="GET", url=url)
        project_settings = response_json["data"]
        return project_settings

    def update_project_settings(
        self,
        max_aoi_size: int = None,
        max_concurrent_jobs: int = None,
        number_of_images=None,
    ) -> None:
        """
        Updates a project's settings.

        Args:
            max_aoi_size: The maximum area of interest geometry size, from 1-1000 sqkm, default 10 sqkm.
            max_concurrent_jobs: The maximum number of concurrent jobs, from 1-10, default 1.
            number_of_images: The maximum number of images returned with each job, from 1-20, default 10.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/settings"
        payload = [
            {
                "name": "JOB_QUERY_MAX_AOI_SIZE",
                "value": f"{100 if max_aoi_size is None else max_aoi_size}",
            },
            {
                "name": "MAX_CONCURRENT_JOBS",
                "value": f"{10 if max_concurrent_jobs is None else max_concurrent_jobs}",
            },
            {
                "name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE",
                "value": f"{10 if number_of_images is None else number_of_images}",
            },
        ]
        self.auth._request(request_type="PUT", url=url, data=payload)
        logger.info("Updated project settings: %s", payload)
