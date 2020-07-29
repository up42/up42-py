from typing import Dict, List, Union
from pathlib import Path

import geojson
from geojson import FeatureCollection

from .auth import Auth
from .job import Job
from .tools import Tools

from .utils import get_logger

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

    def __repr__(self):
        return (
            f"JobCollection(jobs={self.jobs}, project_id={self.project_id}, "
            f"auth={self.auth})"
        )

    # TODO: Make class subscriptable.

    # TODO: Maybe add _jobs_info method?
    # TODO: Maybe add _jobs_status method?

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

        out_filepaths = {}
        for job in self.jobs:
            out_dir = output_directory / f"job_{job.job_id}"
            out_filepaths_job = job.download_results(
                output_directory=out_dir, unpacking=unpacking
            )
            out_filepaths[job.job_id] = out_filepaths_job

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
