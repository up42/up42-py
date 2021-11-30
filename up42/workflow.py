import json
import logging
import copy
from collections import Counter
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
from datetime import datetime

from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
from geojson import Feature, FeatureCollection
from geojson import Polygon as geojson_Polygon
from tqdm import tqdm

from up42.auth import Auth
from up42.job import Job
from up42.estimation import Estimation
from up42.jobcollection import JobCollection
from up42.asset import Asset
from up42.tools import Tools
from up42.utils import (
    get_logger,
    any_vector_to_fc,
    fc_to_query_geometry,
    filter_jobs_on_mode,
    format_time_period,
)

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
    workflow = up42.initialize_workflow(workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98")
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
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}"
        )
        response_json = self.auth._request(request_type="GET", url=url)
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

    def get_compatible_blocks(self) -> dict:
        """
        Gets all compatible blocks for the current workflow. If the workflow is empty
        it will provide all data blocks, if the workflow already has workflow tasks, it
        will provide the compatible blocks for the last workflow task in the workflow.

        Currently no data blocks can be attached to other data blocks.
        """
        tasks: dict = self.get_workflow_tasks(basic=True)  # type: ignore
        if not tasks:
            logger.info("The workflow is empty, returning all data blocks.")

            logging.getLogger("up42.tools").setLevel(logging.CRITICAL)
            data_blocks = Tools(auth=self.auth).get_blocks(
                block_type="data", basic=True
            )
            logging.getLogger("up42.tools").setLevel(logging.INFO)
            return data_blocks  # type: ignore

        last_task = list(tasks.keys())[-1]
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/{self.workflow_id}/"
            f"compatible-blocks?parentTaskName={last_task}"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        compatible_blocks = response_json["data"]["blocks"]
        compatible_blocks = {
            block["name"]: block["blockId"] for block in compatible_blocks
        }
        return compatible_blocks

    def get_workflow_tasks(self, basic: bool = False) -> Union[List, dict]:
        """
        Get the workflow-tasks of the workflow (Blocks in a workflow are called workflow_tasks).

        Args:
            basic: If selected returns a simplified task-name : block-version dict.

        Returns:
            The workflow task info.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}/tasks"
        )

        response_json = self.auth._request(request_type="GET", url=url)
        tasks = response_json["data"]
        logger.info(f"Got {len(tasks)} tasks/blocks in workflow {self.workflow_id}.")

        if basic:
            return {task["name"]: task["blockVersionTag"] for task in tasks}
        else:
            return tasks

    def _construct_full_workflow_tasks_dict(
        self, input_tasks: Union[List]
    ) -> List[dict]:
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
        blocks: dict = Tools(auth=self.auth).get_blocks(basic=False)  # type: ignore
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

    def add_workflow_tasks(self, input_tasks: Union[List[str], List[dict]]) -> None:
        # pylint: disable=line-too-long
        """
        Adds or overwrites workflow tasks in a workflow on UP42.

        Args:
            input_tasks: The blocks to be added to the workflow. Can be a list of the
                block names, block ids (use `up42.get_blocks()`) or block display names
                (The names shown on the [UP42 marketplace](https://marketplace.up42.com).

        !!! Info
            With block names or block display names, the most recent version of a block
            will be added. Using block ids specifies a specific version of a block.

        Examples:
            ```python
            # Block names
            input_tasks = ["sentinelhub-s2", "tiling"]
            ```

            ```python
            # Block Display names
            input_tasks = ["Sentinel-2 Level 2 (BOA) AOI clipped",
                           "Raster Tiling"]
            ```

            ```python
            # Block Ids
            input_tasks = ['018dfb34-fc19-4334-8125-14fd7535f979',
                           '4ed70368-d4e1-4462-bef6-14e768049471']
            ```

        !!! Info "Using Custom Blocks"
            To use a custom block in your workspace, you need to provide the custom block
            id directly in the [full workflow definition](https://docs.up42.com/going-further/api-walkthrough.html#creating-the-the-second-task-processing-block-addition)
            (dict of block id, block name and parent block name). See example below.

        Examples:
            ```python
            # Full workflow definition
            input_tasks = [{'name': 'sentinelhub-s2:1',
                            'parentName': None,
                            'blockId': '018dfb34-fc19-4334-8125-14fd7535f979'},
                           {'name': 'tiling:1',
                            'parentName': 'sentinelhub-s2:1',
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
        logger.info(f"Added tasks to workflow: {input_tasks}")

    def get_parameters_info(self) -> dict:
        """
        Gets infos about the workflow parameters of each block in the current workflow
        to make it easy to construct the desired parameters.

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

    def _get_default_parameters(self) -> dict:
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
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            geojson_Polygon,
            list,
            GeoDataFrame,
            Polygon,
            Point,
        ] = None,
        geometry_operation: Optional[str] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        limit: Optional[int] = None,
        scene_ids: Optional[list] = None,
        assets: Optional[List[Asset]] = None,
    ) -> dict:
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
            start_date: Query period starting day as iso-format string or datetime object,
                e.g. "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".
            end_date: Query period ending day as iso-format or datetime object,
                e.g. "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".
            scene_ids: List of scene_ids, if given ignores all other parameters except geometry.
            assets: Optional, can be used to incorporate existing assets in Storage (result
                of Orders for instance) into new workflows.

        Returns:
            Dictionary of constructed input parameters.
        """
        input_parameters = self._get_default_parameters()
        try:
            data_block_name = list(input_parameters.keys())[0]
        except IndexError as e:
            raise ValueError("The Workflow has no workflow tasks.") from e

        if assets is not None:
            # Needs to be handled in this function(not run_job) as it is only
            # relevant for the data block.
            asset_ids = [asset.asset_id for asset in assets if asset.source == "BLOCK"]
            if not asset_ids:
                raise ValueError(
                    "None of the assets are usable in a workflow since the source is not `BLOCK`."
                )
            input_parameters[data_block_name] = {"asset_ids": asset_ids}
        else:
            if limit is not None:
                input_parameters[data_block_name]["limit"] = limit

            if scene_ids is not None:
                if not isinstance(scene_ids, list):
                    scene_ids = [scene_ids]
                input_parameters[data_block_name]["ids"] = scene_ids
                input_parameters[data_block_name]["limit"] = len(scene_ids)
                input_parameters[data_block_name].pop("time")
            elif start_date is not None or end_date is not None:
                time_period = format_time_period(
                    start_date=start_date, end_date=end_date
                )
                input_parameters[data_block_name]["time"] = time_period

            if geometry is not None:
                aoi_fc = any_vector_to_fc(
                    vector=geometry,
                )
                aoi_feature = fc_to_query_geometry(
                    fc=aoi_fc,
                    geometry_operation=geometry_operation,  # type: ignore
                )

                input_parameters[data_block_name][geometry_operation] = aoi_feature
        return input_parameters

    def construct_parameters_parallel(
        self,
        geometries: List[
            Union[
                dict,
                Feature,
                geojson_Polygon,
                Polygon,
                Point,
            ]
        ] = None,
        interval_dates: List[Tuple[str, str]] = None,
        scene_ids: List[str] = None,
        limit_per_job: int = 1,
        geometry_operation: str = "intersects",
    ) -> List[dict]:
        """
        Maps a list of geometries and a list of time series into a list
        of input parameters of a workflow. If you pass 2 geometries and 1 time
        interval this will result in 2 x 1 input parameters.

        Args:
            geometries: List of unit geometries to map with times.
            interval_dates: List of tuples of start and end dates,
                i.e. `("2014-01-01","2015-01-01")`.
            scene_ids: List of scene ids. Will be mapped 1:1 to each job.
                All other arguments are ignored except geometries if passed.
            limit_per_job: Limit passed to be passed to each individual job parameter.
            geometry_operation: Geometry operation to be passed to each job parameter.

        Returns:
            List of dictionary of constructed input parameters.
        """
        # TODO: Rename arguments
        result_params = []
        # scene_ids mapped to geometries
        if scene_ids is not None and geometries is not None:
            for geo in geometries:
                for scene_id in scene_ids:
                    params = self.construct_parameters(
                        geometry=geo,
                        scene_ids=[scene_id],
                        geometry_operation=geometry_operation,
                    )
                    result_params.append(params)

        # interval_dates mapped to geometries
        elif interval_dates is not None and geometries is not None:
            for geo in geometries:
                for start_date, end_date in interval_dates:
                    params = self.construct_parameters(
                        geometry=geo,
                        geometry_operation=geometry_operation,
                        start_date=start_date,
                        end_date=end_date,
                        limit=limit_per_job,
                    )
                    result_params.append(params)

        # only scene_ids
        elif scene_ids is not None:
            for scene_id in scene_ids:
                result_params.append(
                    self.construct_parameters(
                        geometry=None,
                        scene_ids=[scene_id],
                    )
                )
        else:
            raise ValueError(
                "Please provides geometries and scene_ids, geometries"
                "and time_interval or scene_ids."
            )

        return result_params

    def estimate_job(self, input_parameters: Union[dict, str, Path] = None) -> dict:
        """
        Estimation of price and duration of the workflow for the provided input parameters.

        Args:
            input_parameters: Either json string of workflow parameters or filepath to json.

        Returns:
            A dictionary of estimation for each task in the workflow.
        """
        if input_parameters is None:
            raise ValueError(
                "Select the job_parameters, use workflow.construct_parameters()!"
            )

        workflow_tasks = self.workflow_tasks
        block_names = [task_name.split(":")[0] for task_name in workflow_tasks.keys()]
        input_tasks = self._construct_full_workflow_tasks_dict(block_names)
        for task in input_tasks:
            task["blockVersionTag"] = workflow_tasks[task["name"]]

        estimation = Estimation(
            auth=self.auth, input_parameters=input_parameters, input_tasks=input_tasks
        ).estimate()

        min_credits, max_credits, min_duration, max_duration = [], [], [], []
        for e in estimation.values():
            min_credits.append(e["blockConsumption"]["credit"]["min"])
            max_credits.append(e["blockConsumption"]["credit"]["max"])
            min_credits.append(e["machineConsumption"]["credit"]["min"])
            max_credits.append(e["machineConsumption"]["credit"]["max"])

            min_duration.append(e["machineConsumption"]["duration"]["min"])
            max_duration.append(e["machineConsumption"]["duration"]["max"])

        logger.info(
            f"Estimated: {sum(min_credits)}-{sum(max_credits)} Credits, "
            f"Duration: {int(sum(min_duration) / 60)}-{int(sum(max_duration) / 60)} min."
        )

        return estimation

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

        logger.info(f"Selected input_parameters: {input_parameters}")

        if name is None:
            name = self._info["name"]
        name = f"{name}_py"  # Temporary recognition of python API usage.
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/"
            f"workflows/{self.workflow_id}/jobs?name={name}"
        )
        response_json = self.auth._request(
            request_type="POST", url=url, data=input_parameters  # type: ignore
        )
        job_json = response_json["data"]
        logger.info(f"Created and running new job: {job_json['id']}.")
        job = Job(
            self.auth,
            job_id=job_json["id"],
            project_id=self.project_id,
        )

        if track_status:
            job.track_status()
        return job

    def _helper_run_parallel_jobs(
        self,
        input_parameters_list: List[dict] = None,
        max_concurrent_jobs: int = 10,
        test_job: bool = False,
        name: str = None,
    ) -> "JobCollection":
        """
        Helper function to create and run parallel real or test jobs.

        Args:
            input_parameters_list: List of dictionary of input parameters.
            max_concurrent_jobs: Maximum number of parallel jobs that can be triggered.
            test_job: If set, runs a test query (search for available imagery based on your data parameters).
            name: The job name. Optional, by default the workflow name is assigned.

        Returns:
            The spawned real or test job object.

        Raises:
            ValueError: When max_concurrent_jobs is greater than max_concurrent_jobs set in project settings.
        """
        if input_parameters_list is None:
            raise ValueError(
                "Provide the job parameters via `input_parameters_list`."
                " You can use workflow.construct_parallel_parameters()!"
            )

        if test_job:
            input_parameters_list = copy.deepcopy(input_parameters_list)
            for input_parameters in input_parameters_list:
                input_parameters.update({"config": {"mode": "DRY_RUN"}})  # type: ignore
                logger.info("+++++++++++++++++++++++++++++++++")
                logger.info("Running this job as Test Query...")
                logger.info("+++++++++++++++++++++++++++++++++")

        if name is None:
            name = self._info["name"]

        jobs_list = []
        job_nr = 0

        if max_concurrent_jobs > self.max_concurrent_jobs:
            logger.error(
                f"Maximum concurrent jobs {max_concurrent_jobs} greater "
                f"than project settings {self.max_concurrent_jobs}. "
                "Use project.update_project_settings to change this value."
            )
            raise ValueError("Too many concurrent jobs!")

        # Run all jobs in parallel batches of the max_concurrent_jobs (max. 10.)
        batches = [
            input_parameters_list[pos : pos + max_concurrent_jobs]
            for pos in range(0, len(input_parameters_list), max_concurrent_jobs)
        ]
        for batch in batches:
            batch_jobs = []
            # for params in ten_selected_input_parameters:
            for params in batch:
                logger.info(f"Selected input_parameters: {params}.")

                job_name = (
                    f"{name}_{job_nr}_py"  # Temporary recognition of python API usage.
                )

                url = (
                    f"{self.auth._endpoint()}/projects/{self.project_id}/"
                    f"workflows/{self.workflow_id}/jobs?name={job_name}"
                )
                response_json = self.auth._request(
                    request_type="POST", url=url, data=params
                )
                job_json = response_json["data"]
                logger.info(f"Created and running new job: {job_json['id']}")
                job = Job(
                    self.auth,
                    job_id=job_json["id"],
                    project_id=self.project_id,
                )
                batch_jobs.append(job)
                job_nr += 1

            # Track until all jobs in the batch are finished.
            for job in batch_jobs:
                try:
                    job.track_status(report_time=20)
                except ValueError as e:
                    if str(e) == "Job has failed! See the above log.":
                        logger.warning("Skipping failed job...")
                    else:
                        raise
            jobs_list.extend(batch_jobs)

        job_collection = JobCollection(
            self.auth, project_id=self.project_id, jobs=jobs_list
        )
        return job_collection

    def test_job(
        self,
        input_parameters: Union[Dict, str, Path] = None,
        track_status: bool = False,
        name: str = None,
        get_estimation: bool = False,
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
        if get_estimation:
            self.estimate_job(input_parameters)

        return self._helper_run_job(
            input_parameters=input_parameters,
            test_job=True,
            track_status=track_status,
            name=name,
        )

    def test_jobs_parallel(
        self,
        input_parameters_list: List[dict] = None,
        name: str = None,
        max_concurrent_jobs: int = 10,
    ) -> "JobCollection":
        """
        Create and run test jobs (Test Query) in parallel. With this test query you will not be
        charged with any data or processing credits, but have a preview of the job result.

        Args:
            input_parameters_list: List of dictionary of input parameters
            name: The job name. Optional, by default the workflow name is assigned.
            max_concurrent_jobs: The maximum number of jobs to run in parallel.
                This is defined in the project settings.

        Returns:
            The spawned test JobCollection object.

        Raises:
            ValueError: When max_concurrent_jobs is greater than max_concurrent_jobs set in project settings.
        """
        return self._helper_run_parallel_jobs(
            input_parameters_list=input_parameters_list,
            max_concurrent_jobs=max_concurrent_jobs,
            test_job=True,
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

    def run_jobs_parallel(
        self,
        input_parameters_list: Optional[List[dict]] = None,
        name: str = None,
        max_concurrent_jobs: int = 10,
    ) -> "JobCollection":
        """
        Create and run jobs in parallel.

        Args:
            input_parameters_list: List of dictionary of input parameters
            name: The job name. Optional, by default the workflow name is assigned.
            max_concurrent_jobs: The maximum number of jobs to run in parallel. This is defined in the project settings.

        Returns:
            The spawned JobCollection object.

        Raises:
            ValueError: When max_concurrent_jobs is greater than max_concurrent_jobs set in project settings.
        """
        jobcollection = self._helper_run_parallel_jobs(
            input_parameters_list=input_parameters_list,
            max_concurrent_jobs=max_concurrent_jobs,
            name=name,
        )
        return jobcollection

    def get_jobs(
        self, return_json: bool = False, test_jobs: bool = True, real_jobs: bool = True
    ) -> Union[JobCollection, List[Dict]]:
        """
        Get all jobs associated with the workflow as a JobCollection or json.

        Args:
            return_json: If true, returns the job info jsons instead of a JobCollection.
            test_jobs: Return test jobs or test queries.
            real_jobs: Return real jobs.

        Returns:
            A JobCollection, or alternatively the jobs info as json.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/jobs"
        response_json = self.auth._request(request_type="GET", url=url)
        jobs_json = filter_jobs_on_mode(response_json["data"], test_jobs, real_jobs)

        jobs_workflow_json = [
            j for j in jobs_json if j["workflowId"] == self.workflow_id
        ]

        logger.info(
            f"Got {len(jobs_workflow_json)} jobs for workflow "
            f"{self.workflow_id} in project {self.project_id}."
        )
        if return_json:
            return jobs_workflow_json
        else:
            jobs = [
                Job(self.auth, job_id=job["id"], project_id=self.project_id)
                for job in tqdm(jobs_workflow_json)
            ]
            jobcollection = JobCollection(
                auth=self.auth, project_id=self.project_id, jobs=jobs
            )
            return jobcollection

    def update_name(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> None:
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
        # TODO: Renew info
        logger.info(f"Updated workflow name: {properties_to_update}")

    def delete(self) -> None:
        """
        Deletes the workflow and sets the Python object to None.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/workflows/"
            f"{self.workflow_id}"
        )
        self.auth._request(request_type="DELETE", url=url, return_text=False)
        logger.info(f"Successfully deleted workflow: {self.workflow_id}")
        del self

    @property
    def max_concurrent_jobs(self) -> int:
        """
        Gets the maximum number of concurrent jobs allowed by the project settings.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/settings"
        response_json = self.auth._request(request_type="GET", url=url)
        project_settings = response_json["data"]
        project_settings_dict = {d["name"]: int(d["value"]) for d in project_settings}
        return project_settings_dict["MAX_CONCURRENT_JOBS"]
