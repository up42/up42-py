from pathlib import Path
from typing import Dict, Union, List

import geopandas as gpd
from tqdm import tqdm

from .auth import Auth
from .tools import Tools
from .utils import get_logger, download_results_from_gcs

logger = get_logger(__name__)


# pylint: disable=duplicate-code
class JobTask(Tools):
    def __init__(
        self, auth: Auth, project_id: str, job_id: str, jobtask_id: str,
    ):
        """The JobTask class provides access to the results and parameters of single
        Tasks of UP42 Jobs (each Job contains one or multiple Jobtasks, one for each
        block in the workflow).

        Public Methods:
            get_results_json, download_results, download_quicklooks
        """
        self.auth = auth
        self.project_id = project_id
        self.job_id = job_id
        self.jobtask_id = jobtask_id
        self.quicklooks = None
        self.results = None
        if self.auth.get_info:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"JobTask(jobtask_id={self.jobtask_id}, job={self.job_id}, "
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

    def get_results_json(
        self, as_dataframe: bool = False
    ) -> Union[Dict, gpd.GeoDataFrame]:
        """
        Gets the Jobtask results data.json.

        Args:
            as_dataframe: "fc" for FeatureCollection dict, "df" for GeoDataFrame.

        Returns:
            Json of the results, alternatively geodataframe.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.auth.project_id}/jobs/{self.job_id}"
            f"/tasks/{self.jobtask_id}/outputs/data-json/"
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
            f"/tasks/{self.jobtask_id}/downloads/results/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        download_url = response_json["data"]["url"]
        return download_url

    def download_results(
        self, output_directory: Union[str, Path, None] = None
    ) -> List[str]:
        """
        Downloads and unpacks the jobtask results. Default download to Desktop.

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.
        Returns:
            List of the downloaded results' filepaths.
        """
        # TODO: Overwrite argument
        logger.info("Downloading results of jobtask %s", self.jobtask_id)

        if output_directory is None:
            output_directory = (
                Path.cwd() / f"project_{self.auth.project_id}" / f"job_{self.job_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Download directory: %s", str(output_directory))

        out_filepaths = download_results_from_gcs(
            func_get_download_url=self._get_download_url,
            output_directory=output_directory,
        )

        self.results = out_filepaths
        return out_filepaths

    def download_quicklooks(
        self, output_directory: Union[str, Path, None] = None,
    ) -> List[str]:
        """
        Downloads quicklooks of the job task to disk.

        After download, can be plotted via jobtask.plot_quicklooks().

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.

        Returns:
            The quicklooks filepaths.
        """
        if output_directory is None:
            output_directory = (
                Path.cwd() / f"project_{self.auth.project_id}" / f"job_{self.job_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Download directory: %s", str(output_directory))

        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/{self.jobtask_id}/outputs/quicklooks/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        quicklooks_ids = response_json["data"]

        out_paths: List[str] = []
        for ql_id in tqdm(quicklooks_ids):
            out_path = output_directory / f"quicklook_{ql_id}"  # No suffix required.
            out_paths.append(str(out_path))

            url = (
                f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
                f"/tasks/{self.jobtask_id}/outputs/quicklooks/{ql_id}"
            )
            response = self.auth._request(
                request_type="GET", url=url, return_text=False
            )

            with open(out_path, "wb") as dst:
                for chunk in response:
                    dst.write(chunk)

        self.quicklooks = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths
