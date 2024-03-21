import logging
from typing import Dict, List, Union

from up42.auth import Auth
from up42.host import endpoint
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.utils import filter_jobs_on_mode, get_logger
from up42.workflow import Workflow

logger = get_logger(__name__)


class Project:
    """
    The Project is the top-level class of the UP42 hierarchy. With it you can create
    new workflows, query already existing workflows & jobs in the project and manage
    the project settings.

    ```python
    project = up42.initialize_project(project_id="uz92-8uo0-4dc9-ab1d-06d7ec1a5321")
    ```
    """

    def __init__(self, auth: Auth, project_id: str):
        self.auth = auth
        self.project_id = project_id
        self._info = self.info

    def __repr__(self):
        return (
            f"Project(name: {self._info['name']}, project_id: {self.project_id}, "
            f"description: {self._info['description']}, createdAt: {self._info['createdAt']})"
        )

    @property
    def info(self) -> dict:
        """
        Gets and updates the project metadata information.
        """
        url = endpoint(f"/projects/{self.project_id}")
        response_json = self.auth.request(request_type="GET", url=url)
        self._info = response_json["data"]
        return self._info

    def get_workflows(self, return_json: bool = False) -> Union[List["Workflow"], List[dict]]:
        """
        Gets all workflows in a project as workflow objects or JSON.

        Args:
            return_json: True returns infos of workflows as JSON instead of workflow objects.

        Returns:
            List of Workflow objects in the project or alternatively JSON info of the workflows.
        """
        url = endpoint(f"/projects/{self.project_id}/workflows")
        response_json = self.auth.request(request_type="GET", url=url)
        workflows_json = response_json["data"]
        logger.info(f"Got {len(workflows_json)} workflows for project {self.project_id}.")

        if return_json:
            return workflows_json
        else:
            workflows = [
                Workflow(
                    self.auth,
                    project_id=self.project_id,
                    workflow_id=workflow_json["id"],
                    workflow_info=workflow_json,
                )
                for workflow_json in workflows_json
            ]
            return workflows

    def get_jobs(
        self,
        return_json: bool = False,
        test_jobs: bool = True,
        real_jobs: bool = True,
        limit: int = 500,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> Union[JobCollection, List[dict]]:
        """
        Get all jobs in the project as a JobCollection or JSON.

        Use Workflow().get_job() to get a JobCollection with jobs associated with a
        specific workflow.

        Args:
            return_json: If true, returns the job info JSONs instead of JobCollection.
            test_jobs: Return test jobs or test queries.
            real_jobs: Return real jobs.
            limit: Only return n first jobs by sorting criteria and order, default 500.
            sortby: The sorting criteria, one of "createdAt", "name", "id", "mode", "status", "startedAt", "finishedAt".
            descending: The sorting order, True for descending (default), False for ascending.

        Returns:
            All job objects in a JobCollection, or alternatively the jobs info as JSON.
        """
        allowed_sorting_criteria = [
            "createdAt",
            "name",
            "id",
            "mode",
            "status",
            "startedAt",
            "finishedAt",
        ]
        if sortby not in allowed_sorting_criteria:
            raise ValueError(f"sortby parameter must be one of {allowed_sorting_criteria}!")
        sort = f"{sortby},{'desc' if descending else 'asc'}"

        page = 0
        url = endpoint(f"/projects/{self.project_id}/jobs?page={page}&sort={sort}")
        response_json = self.auth.request(request_type="GET", url=url)
        jobs_json = filter_jobs_on_mode(response_json["data"], test_jobs, real_jobs)

        # API get jobs pagination exhaustion is indicated by empty next page (no last page flag)
        logging.getLogger("up42.utils").setLevel(logging.CRITICAL)
        while len(response_json["data"]) > 0 and len(jobs_json) < limit:
            page += 1
            url = endpoint(f"/projects/{self.project_id}/jobs?page={page}&sort={sort}")
            response_json = self.auth.request(request_type="GET", url=url)
            if len(response_json["data"]) > 0:
                jobs_json.extend(filter_jobs_on_mode(response_json["data"], test_jobs, real_jobs))
        logging.getLogger("up42.utils").setLevel(logging.INFO)
        jobs_json = jobs_json[:limit]
        logger.info(f"Got {len(jobs_json)} jobs (limit parameter {limit}) in project {self.project_id}.")
        if return_json:
            return jobs_json
        else:
            jobs = [
                Job(
                    self.auth,
                    job_id=job_json["id"],
                    project_id=self.project_id,
                    job_info=job_json,
                )
                for job_json in jobs_json
            ]
            jobcollection = JobCollection(auth=self.auth, project_id=self.project_id, jobs=jobs)
            return jobcollection

    def get_project_settings(self) -> List[Dict[str, str]]:
        """
        Gets the project settings.

        Returns:
            The project settings.
        """
        url = endpoint(f"/projects/{self.project_id}/settings")
        response_json = self.auth.request(request_type="GET", url=url)
        project_settings = response_json["data"]
        return project_settings
