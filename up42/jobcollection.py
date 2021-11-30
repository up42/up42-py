from typing import Dict, List, Union, Callable, Any
from pathlib import Path

import geojson
from geojson import FeatureCollection

from up42.auth import Auth
from up42.job import Job
from up42.viztools import VizTools

from up42.utils import get_logger

logger = get_logger(__name__)


class JobCollection(VizTools):
    """
    The JobCollection class provides facilities for handling and downloading
    multiple jobs results as one object.

    A jobcollection is created as the result of e.g. running multiple jobs in parallel:
    ```python
    jobcollection = workflow.run_jobs_parallel()
    ```

    Initialize a jobcollection from existing jobs:
    ```python
    jobcollection = up42.initialize_jobcollection(job_ids=["12345", "6789"])
    ```
    """

    def __init__(self, auth: Auth, project_id: str, jobs: List[Job]):
        self.auth = auth
        self.project_id = project_id
        self.jobs = jobs
        if jobs is not None:
            self.jobs_id = [job.job_id for job in jobs]
        else:
            self.jobs_id = None

    def __repr__(self):
        return f"JobCollection(len: {len(self.jobs)}, jobs: {self.jobs}"

    def __getitem__(self, index: int) -> Job:
        return self.jobs[index]

    def __iter__(self):
        for job in self.jobs:
            yield job

    @property
    def info(self) -> Dict[str, dict]:
        """
        Gets and updates the metadata information for each job in the jobcollection,
            dictionary of job_id : job_information.
        """
        return self.apply(lambda job: job.info, only_succeeded=False)

    @property
    def status(self) -> Dict[str, str]:
        """
        Gets the status for each job in the jobcollection, a dictionary with
        job_id : job status.
        """
        return self.apply(lambda job: job.status, only_succeeded=False)

    def apply(
        self, worker: Callable, only_succeeded: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """
        Helper function to apply `worker` on all jobs in the collection.
        `worker` needs to accept `Job` as first argument. For example, a
        lambda function that returns the job info:
        ```python
        self.apply(lambda job: job.info)
        ```

        Args:
            worker: A function to apply on all jobs in the collection.
            only_succeeded: Only apply to succeeded jobs (default is `True`).
            kwargs: additional keyword arguments to pass to `worker`.
        Returns:
            Dictionary where the key is the job id and the value the return
            of `worker`.
        """
        if not self.jobs:
            raise ValueError(
                "This is an empty JobCollection. Cannot apply over an empty job list."
            )

        out_dict = {}
        for job in self.jobs:
            if only_succeeded:
                if job.is_succeeded:
                    out_dict[job.job_id] = worker(job, **kwargs)
            else:
                out_dict[job.job_id] = worker(job, **kwargs)

        if not out_dict:
            raise ValueError(
                "All jobs have failed! Cannot apply over an empty succeeded job list."
            )

        return out_dict

    # TODO: Add method to get logs of failed jobs

    def download_results(
        self,
        output_directory: Union[str, Path, None] = None,
        merge: bool = True,
        unpacking: bool = True,
    ) -> Dict[str, List[str]]:
        """
        Downloads the job results. The final results are individually downloaded
        and by default a merged data.json is generated with all the results in a single
        feature collection. Unpacking the final will happen as default.
        Args:
            output_directory: The file output directory, defaults to the current working
                directory.
            merge: Wether to generate a merged data.json with all results.
            unpacking: By default the final result which is in TAR archive format will be unpacked.

        Returns:
            Dict of the job_ids and jobs' downloaded results filepaths. In addition,
            an additional key merged_result is added with the path to the merged
            data.json.
        """
        if output_directory is None:
            output_directory = Path.cwd() / f"project_{self.auth.project_id}"
        else:
            output_directory = Path(output_directory)

        def download_results_worker(job, output_directory, unpacking):
            out_dir = output_directory / f"job_{job.job_id}"
            out_filepaths_job = job.download_results(
                output_directory=out_dir, unpacking=unpacking
            )
            return out_filepaths_job

        out_filepaths = self.apply(
            download_results_worker,
            output_directory=output_directory,
            unpacking=unpacking,
        )

        if merge:
            merged_data_json = output_directory / "data.json"
            with open(merged_data_json, "w") as dst:
                out_features = []
                for job_id in out_filepaths:
                    all_files = out_filepaths[job_id]
                    data_json = [d for d in all_files if Path(d).name == "data.json"][0]
                    with open(data_json) as src:
                        data_json_fc = geojson.load(src)
                        for feat in data_json_fc.features:
                            feat.properties["job_id"] = job_id
                            try:
                                feat.properties[
                                    "up42.data_path"
                                ] = f"job_{job_id}/{feat.properties['up42.data_path']}"
                            except KeyError:
                                logger.warning(
                                    "data.json does not contain up42.data_path, skipping..."
                                )
                            out_features.append(feat)
                geojson.dump(FeatureCollection(out_features), dst)

            out_filepaths["merged_result"] = [str(merged_data_json)]

        self.results = out_filepaths
        return out_filepaths
