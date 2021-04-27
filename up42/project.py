import logging
from typing import Dict, List, Union, Optional

from tqdm import tqdm

from up42.auth import Auth
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.utils import get_logger, filter_jobs_on_mode
from up42.workflow import Workflow

logger = get_logger(__name__)


class Project:
    """
    The Project is the top-level class of the UP42 hierarchy. With it you can create
    new workflows, query already existing workflows & jobs in the project and manage
    the project settings.

    Create a new project on the [**UP42 Console website**](authentication.md#authenticate).

    Use an existing project:
    ```python
    up42.authenticate(project_id="uz92-8uo0-4dc9-ab1d-06d7ec1a5321",
                      project_api_key="9i7uec8a-45be-41ad-a50f-98bewb528b10")
    project = up42.initialize_project()
    ```
    """

    def __init__(self, auth: Auth, project_id: str):
        self.auth = auth
        self.project_id = project_id
        self._info = self.info

    def __repr__(self):
        info = self.info
        env = ", env: dev" if self.auth.env == "dev" else ""
        return (
            f"Project(name: {info['name']}, project_id: {self.project_id}, "
            f"description: {info['description']}, createdAt: {info['createdAt']}"
            f"{env})"
        )

    @property
    def info(self) -> dict:
        """
        Gets the project metadata information.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json["data"]
        return response_json["data"]

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
                if workflow._info["name"] == name
                and workflow._info["description"] == description
            ]
            if matching_workflows:
                existing_workflow = matching_workflows[0]
                logger.info(
                    f"Using existing workflow: {name} - {existing_workflow.workflow_id}"
                )
                return existing_workflow

        url = f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
        payload = {"name": name, "description": description}
        response_json = self.auth._request(request_type="POST", url=url, data=payload)
        workflow_id = response_json["data"]["id"]
        logger.info(f"Created new workflow: {workflow_id}")
        workflow = Workflow(
            self.auth, project_id=self.project_id, workflow_id=workflow_id
        )
        return workflow

    def get_workflows(self, return_json: bool = False) -> Union[List["Workflow"], dict]:
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
            f"Got {len(workflows_json)} workflows for project {self.project_id}."
        )

        if return_json:
            return workflows_json
        else:
            workflows = [
                Workflow(self.auth, project_id=self.project_id, workflow_id=work["id"])
                for work in tqdm(workflows_json)
            ]
            return workflows

    def get_jobs(
        self, return_json: bool = False, test_jobs: bool = True, real_jobs: bool = True
    ) -> Union[JobCollection, List[dict]]:
        """
        Get all jobs in the project as a JobCollection or json.

        Use Workflow().get_job() to get a JobCollection with jobs associated with a
        specific workflow.

        Args:
            return_json: If true, returns the job info jsons instead of JobCollection.
            test_jobs: Return test jobs or test queries.
            real_jobs: Return real jobs.

        Returns:
            All job objects in a JobCollection, or alternatively the jobs info as json.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/jobs"
        response_json = self.auth._request(request_type="GET", url=url)
        jobs_json = filter_jobs_on_mode(response_json["data"], test_jobs, real_jobs)
        logger.info(f"Got {len(jobs_json)} jobs in project {self.project_id}.")
        if return_json:
            return jobs_json
        else:
            jobs = [
                Job(self.auth, job_id=job["id"], project_id=self.project_id)
                for job in tqdm(jobs_json)
            ]
            jobcollection = JobCollection(
                auth=self.auth, project_id=self.project_id, jobs=jobs
            )
            return jobcollection

    def get_project_settings(self) -> List[Dict[str, str]]:
        """
        Gets the project settings.

        Returns:
            The project settings.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/settings"
        response_json = self.auth._request(request_type="GET", url=url)
        project_settings = response_json["data"]
        return project_settings

    @property
    def max_concurrent_jobs(self) -> int:
        """
        Gets the maximum number of concurrent jobs allowed by the project settings.
        """
        project_settings = self.get_project_settings()
        project_settings_dict = {d["name"]: int(d["value"]) for d in project_settings}
        return project_settings_dict["MAX_CONCURRENT_JOBS"]

    def update_project_settings(
        self,
        max_aoi_size: Optional[int] = None,
        max_concurrent_jobs: Optional[int] = None,
        number_of_images: Optional[int] = None,
    ) -> None:
        """
        Updates a project's settings.

        Args:
            max_aoi_size: The maximum area of interest geometry size, from 1-1000 sqkm, default 10 sqkm.
            max_concurrent_jobs: The maximum number of concurrent jobs, from 1-10, default 1.
            number_of_images: The maximum number of images returned with each job, from 1-20, default 10.
        """
        # The ranges and default values of the project settings can potentially get
        # increased, so need to be dynamically queried from the server.
        current_settings = {d["name"]: d for d in self.get_project_settings()}

        url = f"{self.auth._endpoint()}/projects/{self.project_id}/settings"
        payload: Dict = {"settings": {}}
        desired_settings = {
            "JOB_QUERY_MAX_AOI_SIZE": max_aoi_size,
            "MAX_CONCURRENT_JOBS": max_concurrent_jobs,
            "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE": number_of_images,
        }

        for name, desired_setting in desired_settings.items():
            if desired_setting is None:
                payload["settings"][name] = str(current_settings[name]["value"])
            else:
                payload["settings"][name] = str(desired_setting)

        self.auth._request(request_type="POST", url=url, data=payload)
        logger.info(f"Updated project settings: {payload}")
