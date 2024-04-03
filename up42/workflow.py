import logging
from collections import Counter
from typing import Dict, List, Optional, Union
from warnings import warn

from tqdm import tqdm

import up42.main as main
from up42.auth import Auth
from up42.host import endpoint
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.utils import filter_jobs_on_mode, get_logger

logger = get_logger(__name__)


class Workflow:
    """
    The Workflow class lets you configure & run jobs and query existing jobs related
    to this workflow.

    Create a new workflow:
    ```python
    workflow = project.create_workflow(name="new_workflow")
    ```

    Use an existing workflow:
    ```python
    workflow = up42.initialize_workflow(
        workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98",
        project_id="uz92-8uo0-4dc9-ab1d-06d7ec1a5321"
    )
    ```
    """

    def __init__(
        self,
        auth: Auth,
        project_id: str,
        workflow_id: str,
        workflow_info: Optional[dict] = None,
    ):
        self.auth = auth
        self.project_id = project_id
        self.workflow_id = workflow_id
        if workflow_info is not None:
            self._info = workflow_info
        else:
            self._info = self.info

    def __repr__(self):
        return (
            f"Workflow(name: {self._info['name']}, workflow_id: {self.workflow_id}, "
            f"description: {self._info['description']}, createdAt: {self._info['createdAt']}, "
            f"project_id: {self.project_id}"
        )

    @property
    def info(self) -> dict:
        """
        Gets and updates the workflow metadata information.
        """
        url = endpoint(f"/projects/{self.project_id}/workflows/{self.workflow_id}")
        response_json = self.auth.request(request_type="GET", url=url)
        self._info = response_json["data"]
        return self._info

    @property
    def workflow_tasks(self) -> Dict[str, str]:
        """
        Gets the building blocks of the workflow as a dictionary with `task_name:block-version`.
        """
        logging.getLogger("up42.workflow").setLevel(logging.CRITICAL)
        workflow_tasks = self.get_workflow_tasks(basic=True)
        logging.getLogger("up42.workflow").setLevel(logging.INFO)
        return workflow_tasks  # type: ignore

    def get_workflow_tasks(self, basic: bool = False) -> Union[List, dict]:
        """
        Get the workflow-tasks of the workflow (Blocks in a workflow are called workflow_tasks).

        Args:
            basic: If selected returns a simplified task-name : block-version dict.

        Returns:
            The workflow task info.
        """
        warn(
            "Workflows are getting deprecated. The current analytics platform will be discontinued "
            "after May 15th, 2024, and will be replaced by new processing functionalities.",
            DeprecationWarning,
            stacklevel=2,
        )
        url = endpoint(f"/projects/{self.project_id}/workflows/{self.workflow_id}/tasks")

        response_json = self.auth.request(request_type="GET", url=url)
        tasks = response_json["data"]
        logger.info(f"Got {len(tasks)} tasks/blocks in workflow {self.workflow_id}.")

        if basic:
            return {task["name"]: task["blockVersionTag"] for task in tasks}
        else:
            return tasks

    def get_parameters_info(self) -> dict:
        """
        Gets infos about the workflow parameters of each block in the current workflow
        to make it easy to construct the desired parameters.

        Returns:
            Workflow parameters info JSON.
        """
        workflow_parameters_info = {}
        workflow_tasks = self.get_workflow_tasks()
        for task in workflow_tasks:
            task_name = task["name"]
            task_default_parameters = task["block"]["parameters"]
            workflow_parameters_info[task_name] = task_default_parameters
        return workflow_parameters_info

    def _get_default_parameters(self) -> dict:
        """
        Gets the default parameters for the workflow that can be directly used to
        run a job.
        """
        default_workflow_parameters = {}

        logger.setLevel(logging.CRITICAL)
        workflow_tasks = self.get_workflow_tasks()
        logger.setLevel(logging.INFO)
        for task in workflow_tasks:
            task_name = task["name"]
            task_parameters = task["block"]["parameters"]

            default_task_parameters = {}
            # Add parameters if they have non-None default or are required (use default or otherwise None)
            for param_name, param_values in task_parameters.items():
                if "default" in param_values:
                    default_task_parameters[param_name] = param_values["default"]
                if "required" in param_values and param_name not in default_task_parameters:
                    # required without default key, add as placeholder
                    if param_values["required"]:
                        default_task_parameters[param_name] = None

            default_workflow_parameters[task_name] = default_task_parameters
        return default_workflow_parameters

    @staticmethod
    def _construct_full_workflow_tasks_dict(input_tasks: Union[List[str], List[dict]]) -> List[dict]:
        """
        Constructs the full workflow task definition from a simplified version.
        Accepts blocks ids, block names, block display names & combinations of them.

        Args:
            input_tasks: List of block names, block ids, or block display names.

        Returns:
            The full workflow task definition.

        Example:
            ```python
            input_tasks = ["sobloo-s2-l1c-aoiclipped",
                           "tiling"]
            ```

            ```python
            input_tasks = ["a2daaab4-196d-4226-a018-a810444dcad1",
                           "4ed70368-d4e1-4462-bef6-14e768049471"]
            ```

            ```python
            input_tasks = ["Sentinel-2 L1C MSI AOI clipped",
                           "Raster Tiling"]
            ```
        """
        full_input_tasks_definition = []

        # Get public + custom blocks.
        logging.getLogger("up42.main").setLevel(logging.CRITICAL)
        blocks: dict = main.get_blocks(basic=False)  # type: ignore
        logging.getLogger("up42.main").setLevel(logging.INFO)

        # Get ids of the input tasks, regardless of the specified format.
        blocks_id_name = {block["id"]: block["name"] for block in blocks}
        blocks_name_id = {block["name"]: block["id"] for block in blocks}
        blocks_displaynames_id = {block["displayName"]: block["id"] for block in blocks}

        input_tasks_ids = []
        for task in input_tasks:
            if task in list(blocks_id_name.keys()):
                input_tasks_ids.append(task)
            elif task in list(blocks_name_id.keys()):
                input_tasks_ids.append(blocks_name_id[task])
            elif task in list(blocks_displaynames_id.keys()):
                input_tasks_ids.append(blocks_displaynames_id[task])
            else:
                raise ValueError(f"The specified input task {task} does not match any available block.")

        # Add first task, the data block.
        data_task = {
            "name": f"{blocks_id_name[input_tasks_ids[0]]}:1",
            "parentName": None,
            "blockId": input_tasks_ids[0],
        }
        full_input_tasks_definition.append(data_task)
        previous_task_name = data_task["name"]

        # All following (processing) blocks.
        for block_id in input_tasks_ids[1:]:
            # Check if multiple of the same block are in the input tasks definition,
            # so that is does not get skipped as it has the same id.
            counts = Counter([x["blockId"] for x in full_input_tasks_definition])
            try:
                count_block = int(counts[block_id]) + 1
            except KeyError:
                count_block = 1

            next_task = {
                "name": f"{blocks_id_name[block_id]}:{count_block}",
                "parentName": previous_task_name,
                "blockId": block_id,
            }
            full_input_tasks_definition.append(next_task)
            previous_task_name = next_task["name"]
        return full_input_tasks_definition

    def get_jobs(
        self,
        return_json: bool = False,
        test_jobs: bool = True,
        real_jobs: bool = True,
    ) -> Union[JobCollection, List[Dict]]:
        """
        Get all jobs associated with the workflow as a JobCollection or JSON.

        Args:
            return_json: If true, returns the job info JSONs instead of a JobCollection.
            test_jobs: Return test jobs or test queries.
            real_jobs: Return real jobs.

        Returns:
            A JobCollection, or alternatively the jobs info as JSON.
        """
        url = endpoint(f"/projects/{self.project_id}/jobs")
        response_json = self.auth.request(request_type="GET", url=url)
        jobs_json = filter_jobs_on_mode(response_json["data"], test_jobs, real_jobs)

        jobs_workflow_json = [j for j in jobs_json if j["workflowId"] == self.workflow_id]

        logger.info(f"Got {len(jobs_workflow_json)} jobs for workflow {self.workflow_id} in project {self.project_id}.")
        if return_json:
            return jobs_workflow_json
        else:
            jobs = [Job(self.auth, job_id=job["id"], project_id=self.project_id) for job in tqdm(jobs_workflow_json)]
            jobcollection = JobCollection(auth=self.auth, project_id=self.project_id, jobs=jobs)
            return jobcollection

    def delete(self) -> None:
        """
        Deletes the workflow and sets the Python object to None.
        """
        url = endpoint(f"/projects/{self.project_id}/workflows/{self.workflow_id}")
        self.auth.request(request_type="DELETE", url=url, return_text=False)
        logger.info(f"Successfully deleted workflow: {self.workflow_id}")
        del self
