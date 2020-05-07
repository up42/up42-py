import json
import logging
from collections import Counter
from pathlib import Path
from typing import Dict, List, Union, Optional

from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
from geojson import Feature, FeatureCollection
from geojson import Polygon as geojson_Polygon
from tqdm import tqdm

from .auth import Auth
from .job import Job
from .tools import Tools
from .utils import get_logger, any_vector_to_fc, fc_to_query_geometry

logger = get_logger(__name__)


class Workflow(Tools):
    def __init__(self, auth: Auth, project_id: str, workflow_id: str):
        """
        The Workflow class can query all available and spawn new jobs for
        an UP42 Workflow and helps to find and set the the workflow tasks, parameters
        and aoi.

        Public Methods:
            get_compatible_blocks, get_workflow_tasks, add_workflow_tasks, get_parameters_info,
            construct_parameters, test_job, run_job, get_jobs, update_name, delete
        """
        self.auth = auth
        self.project_id = project_id
        self.workflow_id = workflow_id
        if self.auth.get_info:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"Workflow(workflow_id={self.workflow_id}, project_id={self.project_id}, "
            f"auth={self.auth}, info={self.info})"
        )

    def _get_info(self) -> Dict:
        """Gets metadata info from an existing workflow"""
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        self.info = response_json["data"]
        return self.info

    def get_compatible_blocks(self) -> Dict:
        """
        Gets all compatible blocks for the current workflow. If the workflow is empty
        it will provide all data blocks, if the workflow already has workflow tasks, it
        will provide the compatible blocks for the last workflow task in the workflow.

        Currently no data blocks can be attached to other data blocks.
        """
        last_task = list(self.get_workflow_tasks(basic=True).keys())[-1]  # type: ignore
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/{self.workflow_id}/"
            f"compatible-blocks?parentTaskName={last_task}"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        compatible_blocks = response_json["data"]["blocks"]
        # TODO: Plot diagram of current workflow in green, attachable blocks in red.
        compatible_blocks = {
            block["name"]: block["blockId"] for block in compatible_blocks
        }
        return compatible_blocks

    def get_workflow_tasks(self, basic: bool = False) -> Union[List, Dict]:
        """
        Get the workflow-tasks of the workflow (Blocks in a workflow are called workflow_tasks)

        Args:
            basic: If selected returns a simplified task-name : task-id` version.

        Returns:
            The workflow task info.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}/tasks"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        tasks = response_json["data"]
        logger.info("Got %s tasks/blocks in workflow %s.", len(tasks), self.workflow_id)

        if basic:
            return {task["name"]: task["id"] for task in tasks}
        else:
            return tasks

    def _construct_full_workflow_tasks_dict(
        self, input_tasks: Union[List]
    ) -> List[Dict]:
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
        logging.getLogger("up42.tools").setLevel(logging.CRITICAL)
        blocks: Dict = self.get_blocks(basic=False)  # type: ignore
        logging.getLogger("up42.tools").setLevel(logging.INFO)

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
                raise ValueError(
                    f"The specified input task {task} does not match any "
                    f"available block."
                )

        # Add first task, the data block.
        data_task = {
            "name": f"{blocks_id_name[input_tasks_ids[0]]}:1",
            "parentName": None,
            "blockId": input_tasks_ids[0],
        }
        full_input_tasks_definition.append(data_task)
        previous_task_name = data_task["name"]

        # All all following (processing) blocks.
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

    def add_workflow_tasks(self, input_tasks: Union[List[str], List[Dict]]) -> None:
        """
        Adds or overwrites workflow tasks in a workflow on UP42.

        Args:
            input_tasks: The input tasks, specifying the blocks. Can be a list of the
                block ids, block names or block display names (The name shown on the
                [marketplace](https://marketplace.up42.com).

        !!! Info
            Using block ids specifies a specific version of the block that will be added
            to the workflow. With block names or block display names, the most recent
            version of a block will always be added.

        Example:
            ```python
            input_tasks_simple = ['a2daaab4-196d-4226-a018-a810444dcad1',
                                  '4ed70368-d4e1-4462-bef6-14e768049471']
            ```

            ```python
            input_tasks = ["sobloo-s2-l1c-aoiclipped", "tiling"]
            ```

            ```python
            input_tasks = ["Sentinel-2 L1C MSI AOI clipped",
                           "Raster Tiling"]


        Optional: The input_tasks can also be provided as the full, detailed workflow task
        definition (dict of block id, block name and parent block name). Always use :1
        to be able to identify the order when two times the same workflow task is used.
        The name is arbitrary, but best use the block name.

        Example:
            ```python
            input_tasks_full = [{'name': 'sobloo-s2-l1c-aoiclipped:1',
                                 'parentName': None,
                                 'blockId': 'a2daaab4-196d-4226-a018-a810444dcad1'},
                                {'name': 'sharpening:1',
                                 'parentName': 'sobloo-s2-l1c-aoiclipped',
                                 'blockId': '4ed70368-d4e1-4462-bef6-14e768049471'}]
            ```
        """
        # Construct proper task definition from simplified input.
        if isinstance(input_tasks[0], str) and not isinstance(input_tasks[0], dict):
            input_tasks = self._construct_full_workflow_tasks_dict(input_tasks)

        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}/tasks/"
        )
        self.auth._request(request_type="POST", url=url, data=input_tasks)
        logger.info("Added tasks to workflow: %r", input_tasks)

    def get_parameters_info(self) -> Dict:
        """
        Gets infos about the workflow parameters of each block in the workflow to
        make it easy to construct the desired parameters.

        Returns:
            Workflow parameters info json.
        """
        workflow_parameters_info = {}
        workflow_tasks = self.get_workflow_tasks()
        for task in workflow_tasks:
            task_name = task["name"]
            task_default_parameters = task["block"]["parameters"]
            workflow_parameters_info[task_name] = task_default_parameters
        return workflow_parameters_info

    def _get_default_parameters(self) -> Dict:
        """
        Gets the default parameters for the workflow that can be directly used to
        run a job. Excludes geometry operation and geometry of the data block.
        """
        default_workflow_parameters = {}

        logger.setLevel(logging.CRITICAL)
        workflow_tasks = self.get_workflow_tasks()
        logger.setLevel(logging.INFO)
        for task in workflow_tasks:
            task_name = task["name"]
            task_parameters = task["block"]["parameters"]

            default_task_parameters = {}

            for param_name, param_values in task_parameters.items():
                if "default" in param_values and param_values["default"] is not None:
                    default_task_parameters[param_name] = param_values["default"]

            default_workflow_parameters[task_name] = default_task_parameters
        return default_workflow_parameters

    def construct_parameters(
        self,
        geometry: Optional[
            Union[
                Dict,
                Feature,
                FeatureCollection,
                geojson_Polygon,
                List,
                GeoDataFrame,
                Polygon,
                Point,
            ]
        ] = None,
        geometry_operation: Optional[str] = None,
        handle_multiple_features: str = "footprint",
        start_date: str = None,  # TODO: Other format? More time options?
        end_date: str = None,
        limit: int = None,
        scene_ids: List = None,
        order_ids: List[str] = None,
    ) -> Dict:
        """
        Constructs workflow input parameters with a specified aoi, the default input parameters, and
        optionally limit and order-ids. Further parameter editing needs to be done manually
        via dict.update({key:value}).

        Args:
            geometry: One of Dict, FeatureCollection, Feature, List,
                GeoDataFrame, shapely.geometry.Polygon, shapely.geometry.Point. All
                assume EPSG 4326.
            geometry_operation: Desired operation, One of "bbox", "intersects", "contains".
            limit: Maximum number of expected results.
            start_date: Query period starting day, format "2020-01-01".
            end_date: Query period ending day, format "2020-01-01".
            scene_ids: List of scene_ids, if given ignores all other parameters except geometry.
            order_ids: Optional, can be used to incorporate existing bought imagery on UP42
                into new workflows.

        Returns:
            Dictionary of constructed input parameters.
        """
        # TODO: Add ipy slide widget option? One for each block.
        input_parameters = self._get_default_parameters()
        data_block_name = list(input_parameters.keys())[0]

        if order_ids is not None:
            # Needs to be handled in this function(not run_job) as it is only
            # relevant for the data block.
            # TODO: Check for order-id correct schema, should be handled on backend?
            input_parameters[data_block_name] = {"order_ids": order_ids}
        else:
            if limit is not None:
                input_parameters[data_block_name]["limit"] = limit
            if scene_ids is not None:
                if not isinstance(scene_ids, list):
                    scene_ids = [scene_ids]
                input_parameters[data_block_name]["ids"] = scene_ids
                input_parameters[data_block_name]["limit"] = len(scene_ids)
                input_parameters[data_block_name].pop("time")
                # TODO: In case of ids remove all non-relevant parameters. Cleaner.
            elif start_date is not None and end_date is not None:
                datetime = f"{start_date}T00:00:00Z/{end_date}T00:00:00Z"
                input_parameters[data_block_name]["time"] = datetime
            aoi_fc = any_vector_to_fc(vector=geometry,)
            aoi_feature = fc_to_query_geometry(
                fc=aoi_fc,
                geometry_operation=geometry_operation,  # type: ignore
                squash_multiple_features=handle_multiple_features,
            )

            input_parameters[data_block_name][geometry_operation] = aoi_feature
        return input_parameters

    def _helper_run_job(
        self,
        input_parameters: Union[Dict, str, Path] = None,
        test_job=False,
        track_status: bool = False,
        name: str = None,
    ) -> "Job":
        """
        Helper function to create and run a new real or test job.

        Args:
            input_parameters: Either json string of workflow parameters or filepath to json.
            test_job: If set, runs a test query (search for available imagery based on your data parameters).
            track_status: Automatically attaches workflow.track_status which queries
                the job status every 30 seconds.
            name: The job name. Optional, by default the workflow name is assigned.

        Returns:
            The spawned real or test job object.
        """
        if input_parameters is None:
            raise ValueError(
                "Select the job_parameters, use workflow.construct_parameters()!"
            )

        if isinstance(input_parameters, (str, Path)):
            with open(input_parameters) as src:
                input_parameters = json.load(src)
            logger.info("Loading job parameters from json file.")

        if test_job:
            input_parameters = input_parameters.copy()  # type: ignore
            input_parameters.update({"config": {"mode": "DRY_RUN"}})  # type: ignore
            logger.info("+++++++++++++++++++++++++++++++++")
            logger.info("Running this job as Test Query...")
            logger.info("+++++++++++++++++++++++++++++++++")

        logger.info("Selected input_parameters: %s.", input_parameters)

        if name is None:
            name = self.info["name"]
        name = f"{name}_py"  # Temporary recognition of python API usage.
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/"
            f"workflows/{self.workflow_id}/jobs?name={name}"
        )
        response_json = self.auth._request(
            request_type="POST", url=url, data=input_parameters
        )
        job_json = response_json["data"]
        logger.info("Created and running new job: %s.", job_json["id"])
        job = Job(self.auth, job_id=job_json["id"], project_id=self.project_id,)

        if track_status:
            job.track_status()
        return job

    def test_job(
        self,
        input_parameters: Union[Dict, str, Path] = None,
        track_status: bool = False,
        name: str = None,
    ) -> "Job":
        """
        Create a run a new test job (Test Query). With this test query you will not be
        charged with any data or processing credits, but have a preview of the job result.

        Args:
            input_parameters: Either json string of workflow parameters or filepath to json.
            track_status: Automatically attaches workflow.track_status which queries
                the job status every 30 seconds.
            name: The job name. Optional, by default the workflow name is assigned.

        Returns:
            The spawned test job object.
        """
        return self._helper_run_job(
            input_parameters=input_parameters,
            test_job=True,
            track_status=track_status,
            name=name,
        )

    def run_job(
        self,
        input_parameters: Union[Dict, str, Path] = None,
        track_status: bool = False,
        name: str = None,
    ) -> "Job":
        """
        Creates and runs a new job.

        Args:
            input_parameters: Either json string of workflow parameters or filepath to json.
            track_status: Automatically attaches workflow.track_status which queries
                the job status every 30 seconds.
            name: The job name. Optional, by default the workflow name is assigned.

        Returns:
            The spawned job object.
        """
        return self._helper_run_job(
            input_parameters=input_parameters, track_status=track_status, name=name
        )

    def get_jobs(self, return_json: bool = False) -> Union[List["Job"], Dict]:
        """
        Get all jobs associated with the workflow as job objects or json.

        Args:
            return_json: If true, returns the job info jsons instead of job objects.

        Returns:
            All job objects as a list, or alternatively the jobs info as json.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/jobs"
        response_json = self.auth._request(request_type="GET", url=url)
        jobs_json = response_json["data"]

        jobs_workflow_json = [
            j for j in jobs_json if j["workflowId"] == self.workflow_id
        ]

        logger.info(
            "Got %s jobs for workflow %s in project %s.",
            len(jobs_workflow_json),
            self.workflow_id,
            self.project_id,
        )
        if return_json:
            return jobs_workflow_json
        else:
            jobs = [
                Job(self.auth, job_id=job["id"], project_id=self.project_id)
                for job in tqdm(jobs_workflow_json)
            ]
            return jobs

    def update_name(self, name: str = None, description: str = None) -> None:
        """
        Updates the workflow name and description.

        Args:
            name: New name of the workflow.
            description: New description of the workflow.
        """
        properties_to_update = {"name": name, "description": description}
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}"
        )
        self.auth._request(request_type="PUT", url=url, data=properties_to_update)
        logger.info("Updated workflow name: %r", properties_to_update)

    def delete(self) -> None:
        """
        Deletes the workflow and sets the Python object to None.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}"
        )
        self.auth._request(request_type="DELETE", url=url, return_text=False)
        logger.info("Successfully deleted workflow: %s", self.workflow_id)
        del self
