import logging
from pathlib import Path
from time import sleep
from typing import List, Union, Optional

from geopandas import GeoDataFrame
import requests
import requests.exceptions

from up42.auth import Auth
from up42.jobtask import JobTask
from up42.viztools import VizTools
from up42.utils import (
    get_logger,
    download_results_from_gcs,
    download_results_from_gcs_without_unpacking,
)

logger = get_logger(__name__)


# pylint: disable=duplicate-code
class Job(VizTools):
    """
    The Job class is the result of running a workflow. It lets you download, visualize and
        manipulate the results of the job, and keep track of the status or cancel a job while
        still running.

    Run a new job:
    ```python
    job = workflow.run_job(name="new_job", input_parameters={...})
    ```

    Use an existing job:
    ```python
    job = up42.initialize_job(job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021")
    ```
    """

    def __init__(
        self, auth: Auth, project_id: str, job_id: str, job_info: Optional[dict] = None
    ):

        self.auth = auth
        self.project_id = project_id
        self.job_id = job_id
        self.quicklooks = None
        self.results = None
        if job_info is not None:
            self._info = job_info
        else:
            self._info = self.info

    def __repr__(self):
        return (
            f"Job(name: {self._info['name']}, job_id: {self.job_id}, mode: {self._info['mode']}, "
            f"status: {self._info['status']}, startedAt: {self._info['startedAt']}, "
            f"finishedAt: {self._info['finishedAt']}, workflow_name: {self._info['workflowName']}, "
            f"input_parameters: {self._info['inputs']}"
        )

    @property
    def info(self) -> dict:
        """
        Gets and updates the job metadata information.
        """
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json["data"]
        return self._info

    @property
    def status(self) -> str:
        """
        Gets the job progress status. One of `SUCCEEDED`, `NOT STARTED`, `PENDING`,
            `RUNNING`, `CANCELLED`, `CANCELLING`, `FAILED`, `ERROR`.
        """
        status = self.info["status"]
        logger.info(f"Job is {status}")
        return status

    @property
    def is_succeeded(self) -> bool:
        """
        Gets `True` if the job succeeded, `False` otherwise.
        Also see [status attribute](job-reference.md#up42.job.Job.status).
        """
        return self.status == "SUCCEEDED"

    def track_status(self, report_time: int = 30) -> str:
        """`
        Continuously gets the job status until job has finished or failed.

        Internally checks every five seconds for the status, prints the log every
        time interval given in report_time argument.

        Args:
            report_time: The intervall (in seconds) when to query the job status.
        """
        logger.info(
            f"Tracking job status continuously, reporting every {report_time} seconds...",
        )
        status = "NOT STARTED"
        time_asleep = 0

        while status != "SUCCEEDED":
            logger.setLevel(logging.CRITICAL)
            status = self.status
            logger.setLevel(logging.INFO)

            # TODO: Add statuses as constants (maybe objects?)
            if status in ["NOT STARTED", "PENDING", "RUNNING"]:
                if time_asleep != 0 and time_asleep % report_time == 0:
                    logger.info(f"Job is {status}! - {self.job_id}")
            elif status in ["FAILED", "ERROR"]:
                logger.info(f"Job is {status}! - {self.job_id} - Printing logs ...")
                self.get_logs(as_print=True)
                raise ValueError("Job has failed! See the above log.")
            elif status in ["CANCELLED", "CANCELLING"]:
                logger.info(f"Job is {status}! - {self.job_id}")
                raise ValueError("Job has been cancelled!")
            elif status == "SUCCEEDED":
                logger.info(f"Job finished successfully! - {self.job_id}")

            sleep(5)
            time_asleep += 5

        return status

    def cancel_job(self) -> None:
        """Cancels a pending or running job."""
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}/cancel/"
        self.auth._request(request_type="POST", url=url)
        logger.info(f"Job canceled: {self.job_id}")

    def download_quicklooks(
        self, output_directory: Union[str, Path, None] = None
    ) -> List[str]:
        """
        Conveniance function that downloads the quicklooks of the data (dirst) jobtask.

        After download, can be plotted via job.plot_quicklooks().
        """
        # Currently only the first/data task produces quicklooks.
        logger.setLevel(logging.CRITICAL)
        data_task = self.get_jobtasks()[0]
        logger.setLevel(logging.INFO)

        out_paths: List[str] = data_task.download_quicklooks(  # type: ignore
            output_directory=output_directory
        )  # type: ignore
        self.quicklooks = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths

    def get_results_json(self, as_dataframe: bool = False) -> Union[dict, GeoDataFrame]:
        """
        Gets the Job results data.json.

        Args:
            as_dataframe: Return type, Default Feature Collection. GeoDataFrame if True.

        Returns:
            The job data.json json.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/outputs/data-json/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        logger.info(f"Retrieved {len(response_json['features'])} features.")

        if as_dataframe:
            # UP42 results are always in EPSG 4326
            df = GeoDataFrame.from_features(response_json, crs=4326)
            return df
        else:
            return response_json

    def _get_download_url(self) -> str:
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/downloads/results/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        download_url = response_json["data"]["url"]
        return download_url

    def download_results(
        self, output_directory: Union[str, Path, None] = None, unpacking: bool = True
    ) -> List[str]:
        """
        Downloads the job results. Unpacking the final file will happen as default.

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.
            unpacking: By default the final result which is in TAR archive format will be unpacked.

        Returns:
            List of the downloaded results' filepaths.
        """
        logger.info(f"Downloading results of job {self.job_id}")

        if output_directory is None:
            output_directory = (
                Path.cwd() / f"project_{self.auth.project_id}/job_{self.job_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

        download_url = self._get_download_url()
        if unpacking:
            out_filepaths = download_results_from_gcs(
                download_url=download_url,
                output_directory=output_directory,
            )
        else:
            out_filepaths = download_results_from_gcs_without_unpacking(
                download_url=download_url,
                output_directory=output_directory,
            )

        self.results = out_filepaths
        return out_filepaths

    def upload_results_to_bucket(
        self,
        gs_client,
        bucket,
        folder: str,
        extension: str = ".tgz",
        version: str = "v0",
    ) -> None:
        """
        Uploads the results of a job directly to a custom google cloud storage bucket.
        """
        download_url = self._get_download_url()
        r = requests.get(download_url)
        blob = bucket.blob(
            str(Path(version) / Path(folder) / Path(self.job_id + extension))
        )
        logger.info(f"Upload job {self.job_id} results to {blob.name} ...")
        blob.upload_from_string(
            data=r.content,
            content_type="application/octet-stream",
            client=gs_client,
        )
        logger.info("Uploaded!")

    def get_logs(
        self, as_print: bool = True, as_return: bool = False
    ) -> Optional[dict]:
        """
        Convenience function to print or return the logs of all job tasks.

        Args:
            as_print: Prints the logs, no return.
            as_return: Also returns the log strings.

        Returns:
            The log strings (only if as_return was selected).
        """
        job_logs = {}

        jobtasks: List[dict] = self.get_jobtasks(return_json=True)  # type: ignore
        jobtasks_ids = [task["id"] for task in jobtasks]

        logger.info(f"Getting logs for {len(jobtasks_ids)} job tasks: {jobtasks_ids}")
        if as_print:
            print(
                f"Printing logs of {len(jobtasks_ids)} JobTasks in Job with job_id "
                f"{self.job_id}:\n"
            )

        for idx, jobtask_id in enumerate(jobtasks_ids):
            url = (
                f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/"
                f"{self.job_id}/tasks/{jobtask_id}/logs"
            )
            response_json = self.auth._request(request_type="GET", url=url)

            job_logs[jobtask_id] = response_json

            if as_print:
                print("----------------------------------------------------------")
                print(f"JobTask {idx+1} with jobtask_id {jobtask_id}:\n")
                print(response_json)
        if as_return:
            return job_logs
        else:
            return None

    def get_jobtasks(
        self, return_json: bool = False
    ) -> Union[List["JobTask"], List[dict]]:
        """
        Get the individual items of the job as a list of JobTask objects or json.

        Args:
            return_json: If True returns the json information of the job tasks.

        Returns:
            The job task objects in a list.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/"
        )
        logger.info(f"Getting job tasks: {self.job_id}")
        response_json = self.auth._request(request_type="GET", url=url)
        jobtasks_json: List[dict] = response_json["data"]

        if return_json:
            return jobtasks_json
        else:
            jobtasks = [
                JobTask(
                    auth=self.auth,
                    project_id=self.project_id,
                    job_id=self.job_id,
                    jobtask_id=task["id"],
                )
                for task in jobtasks_json
            ]
            return jobtasks

    def get_jobtasks_results_json(self) -> dict:
        """
        Convenience function to get the resulting data.json of all job tasks
        in a dictionary of strings.

        Returns:
            The data.json of alle single job tasks.
        """
        jobtasks: List[dict] = self.get_jobtasks(return_json=True)  # type: ignore
        jobtasks_ids = [task["id"] for task in jobtasks]
        jobtasks_results_json = {}
        for jobtask_id in jobtasks_ids:
            url = (
                f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
                f"/tasks/{jobtask_id}/outputs/data-json"
            )
            response_json = self.auth._request(request_type="GET", url=url)

            jobtasks_results_json[jobtask_id] = response_json
        return jobtasks_results_json
