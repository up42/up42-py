from pathlib import Path
from typing import Union, List

from geopandas import GeoDataFrame
from tqdm import tqdm

from up42.auth import Auth
from up42.viztools import VizTools
from up42.utils import get_logger, download_results_from_gcs

logger = get_logger(__name__)


# pylint: disable=duplicate-code
class JobTask(VizTools):
    """
    The JobTask class provides access to the result of a specific block in the workflow.
    Each job contains one or multiple JobTasks, one for each block.

    Use an existing jobtask:
    ```python
    jobtask = up42.initialize_jobtask(jobtask_id="3f772637-09aa-4164-bded-692fcd746d20",
                                      job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021")
    ```
    """

    def __init__(
        self,
        auth: Auth,
        project_id: str,
        job_id: str,
        jobtask_id: str,
    ):
        self.auth = auth
        self.project_id = project_id
        self.job_id = job_id
        self.jobtask_id = jobtask_id
        self.quicklooks = None
        self.results = None
        self._info = self.info

    def __repr__(self):
        return (
            f"JobTask(name: {self._info['name']}, jobtask_id: {self.jobtask_id}, "
            f"status: {self._info['status']}, startedAt: {self._info['startedAt']}, "
            f"finishedAt: {self._info['finishedAt']}, job_name: {self._info['name']}, "
            f"block_name: {self._info['block']['name']}, block_version: {self._info['blockVersion']}"
        )

    @property
    def info(self) -> dict:
        """
        Gets and updates the jobtask metadata information.
        """
        url = (
            f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/"
        )
        response_json = self.auth._request(request_type="GET", url=url)
        info_all_jobtasks = response_json["data"]
        self._info = next(
            item for item in info_all_jobtasks if item["id"] == self.jobtask_id
        )
        return self._info

    def get_results_json(self, as_dataframe: bool = False) -> Union[dict, GeoDataFrame]:
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
        logger.info(f"Retrieved {len(response_json['features'])} features.")

        if as_dataframe:
            # UP42 results are always in EPSG 4326
            df = GeoDataFrame.from_features(response_json, crs=4326)
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
        logger.info(f"Downloading results of jobtask {self.jobtask_id}")

        if output_directory is None:
            output_directory = (
                Path.cwd()
                / f"project_{self.auth.project_id}/job_{self.job_id}/jobtask_{self.jobtask_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

        download_url = self._get_download_url()
        out_filepaths = download_results_from_gcs(
            download_url=download_url,
            output_directory=output_directory,
        )

        self.results = out_filepaths
        return out_filepaths

    def download_quicklooks(
        self,
        output_directory: Union[str, Path, None] = None,
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
            # On purpose downloading the quicklooks to the jobs folder and not the
            # jobtasks folder,since only relevant for data block task. And clearer
            # for job.download_quicklooks.
            output_directory = (
                Path.cwd() / f"project_{self.auth.project_id}" / f"job_{self.job_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

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
