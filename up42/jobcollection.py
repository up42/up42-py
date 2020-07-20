from typing import Dict, List, Union
from pathlib import Path

from .auth import Auth
from .job import Job
from .tools import Tools

from .utils import (
    get_logger,
    download_results_from_gcs,
    download_results_from_gcs_without_unpacking,
)

logger = get_logger(__name__)

# pylint: disable=duplicate-code
class JobCollection(Tools):
    def __init__(self, auth: Auth, project_id: str, jobs: List[Job]):
        """
        The JobCollection class provides facilities for downloading and merging
        multiple jobs results.
        """
        self.auth = auth
        self.project_id = project_id
        self.jobs = jobs
        if jobs is not None:
            self.jobs_id = [job.job_id for job in jobs]
        else:
            self.jobs_id = None
        # self.jobs_id = self._jobs_id()

    def __repr__(self):
        return (
            f"JobCollection(jobs={self.jobs}, project_id={self.project_id}, "
            f"auth={self.auth})"
        )

    # TODO: Maybe add _jobs_info method?
    # TODO: Maybe add _jobs_status method?

    def _jobs_id(self):
        jobs_id = []
        for job in self.jobs:
            jobs_id.append(job.job_id)

        self.jobs_id = jobs_id
        return self.jobs_id

    def _get_download_url(self, job_id) -> str:
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{job_id}"
            f"/downloads/results/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        download_url = response_json["data"]["url"]
        return download_url

    def download_parallel_results(
        self, output_directory: Union[str, Path, None] = None, unpacking: bool = True
    ) -> Dict[str, List[str]]:
        """
        Downloads the job results. Unpacking the final will happen as default. However
        please note in the case of exotic formats like SAFE or DIMAP, the final result should not be unpacked.

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.
            unpacking: By default the final result which is in TAR archive format will be unpacked.

        Returns:
            List of the downloaded results' filepaths.
        """
        if output_directory is None:
            output_directory = Path.cwd() / f"project_{self.auth.project_id}"
        else:
            output_directory = Path(output_directory)

        out_filepaths = {}
        for job_id in self.jobs_id:
            # TODO: Overwrite argument
            logger.info("Downloading results of job %s", job_id)

            output_directory_id = output_directory / f"job_{job_id}"
            output_directory_id.mkdir(parents=True, exist_ok=True)
            logger.info("Download directory: %s", str(output_directory_id))

            download_url = self._get_download_url(job_id)
            if unpacking:
                out_filepaths[job_id] = download_results_from_gcs(
                    download_url=download_url, output_directory=output_directory_id,
                )
            else:
                out_filepaths[job_id] = download_results_from_gcs_without_unpacking(
                    download_url=download_url, output_directory=output_directory_id,
                )

        self.results = out_filepaths
        return out_filepaths
