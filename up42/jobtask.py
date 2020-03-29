import os
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, Union, List

import geopandas as gpd
import requests
import requests.exceptions

from .auth import Auth
from .tools import Tools
from .utils import get_logger

logger = get_logger(__name__)  # level=logging.CRITICAL  #INFO


class JobTask(Tools):
    def __init__(
        self, auth: Auth, project_id: str, job_id: str, job_task_id: str,
    ):
        """The JobTask class provides access to the results and parameters of single
        Tasks of UP42 Jobs (each Job contains one or multiple Jobtasks, one for each
        block in the workflow).

        Public Methods:
            get_result_json, download_result, download_quicklook
        """
        self.auth = auth
        self.project_id = project_id
        self.job_id = job_id
        self.job_task_id = job_task_id
        if self.auth.get_info:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"JobTask(job_task_id={self.job_task_id}, job={self.job_id}, "
            f"auth={self.auth}, info={self.info})"
        )

    def _get_info(self):
        """Gets metadata info from an existing Job"""
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        self.info = response_json["data"]
        return self.info

    def get_result_json(
        self, as_dataframe: bool = False
    ) -> Union[Dict, gpd.GeoDataFrame]:
        """
        Gets the Jobtask result data.json.

        Args:
            as_dataframe: "fc" for FeatureCollection dict, "df" for GeoDataFrame.

        Returns:
            Json of the results, alternatively geodataframe.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.auth.project_id}/jobs/{self.job_id}"
            f"/tasks/{self.job_task_id}/outputs/data-json/"
        )
        response_json = self.auth._request(request_type="GET", url=url)

        if as_dataframe:
            # UP42 results are always in EPSG 4326
            df = gpd.GeoDataFrame.from_features(response_json, crs=4326)
            return df
        else:
            return response_json

    def _get_download_url(self):
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/{self.job_task_id}/downloads/results/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        download_url = response_json["data"]["url"]
        return download_url

    def download_result(self, out_dir: Union[str, Path] = None) -> None:
        """
        Downloads and unpacks the job task result. Default download to Desktop.

        Args:
            out_dir: The output directory for the downloaded files.
        """
        download_url = self._get_download_url()

        # TODO: Add tdqm progress bar

        if out_dir is None:
            out_dir = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        logger.info("Downloading results of job %s", self.job_id)

        tgz_file = tempfile.mktemp()
        with open(tgz_file, "wb") as f:
            r = requests.get(download_url)
            f.write(r.content)
        with tarfile.open(tgz_file) as tgz:
            files = tgz.getmembers()
            tif_files = [i for i in files if i.isfile() and i.name.endswith(".tif")]
            out_filepaths = []
            for count, f in enumerate(tif_files):
                out = tgz.extractfile(f)
                out_file = out_dir / Path(f"{self.job_id}_{count}.tif")
                with open(out_file, "wb") as o:
                    o.write(out.read())
                out_filepaths.append(str(out_file))

        logger.info("Download successful of files %s", out_filepaths)
        return out_filepaths

    def download_quicklook(self, out_dir: Union[str, Path] = None,) -> List[Path]:
        """
        Downloads quicklooks of all job tasks to disk.

        After download, can be plotted via jobtask.plot_quicklook().

        Args:
            out_dir: Output directory.

        Returns:
            The quicklooks filepaths.
        """
        if out_dir is None:
            out_dir = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/{self.job_task_id}/outputs/quicklooks/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        quicklook_ids = response_json["data"]

        out_paths = []
        for ql_id in quicklook_ids:
            out_path = Path(out_dir) / f"quicklook_{ql_id}.jpg"
            out_paths.append(out_path)

            url = (
                f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
                f"/tasks/{self.job_task_id}/outputs/quicklooks/{ql_id}"
            )
            response = self.auth._request(
                request_type="GET", url=url, return_text=False
            )

            with open(out_path, "wb") as dst:
                for chunk in response:
                    dst.write(chunk)

        self.quicklook = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths
