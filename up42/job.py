import logging
from pathlib import Path
from time import sleep
from typing import Dict, List, Union, Optional

import folium
from geopandas import GeoDataFrame
import geopandas as gpd
import numpy as np
import requests
import requests.exceptions
from shapely.geometry import box
from rasterio.vrt import WarpedVRT
import rasterio

from up42.auth import Auth
from up42.jobtask import JobTask
from up42.tools import Tools
from up42.utils import (
    get_logger,
    folium_base_map,
    download_results_from_gcs,
    download_results_from_gcs_without_unpacking,
)

try:
    from IPython.display import display
    from IPython import get_ipython
except ImportError:
    # No Ipython installed, Installed but run in shell
    pass

logger = get_logger(__name__)


# pylint: disable=duplicate-code
class Job(Tools):
    def __init__(
        self, auth: Auth, project_id: str, job_id: str, order_ids: List[str] = None,
    ):
        """
        The Job class provides access to the results, parameters and tasks of UP42
        Jobs (Workflows that have been run as Jobs).
        """
        self.auth = auth
        self.project_id = project_id
        self.job_id = job_id
        self.quicklooks = None
        self.results = None
        self.order_ids = order_ids
        if self.auth.get_info:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"Job(job_id={self.job_id}, project_id={self.project_id}, "
            f"order_ids={self.order_ids}, auth={self.auth}, info={self.info})"
        )

    def _get_info(self):
        """Gets metadata info from an existing Job"""
        url = f"{self.auth._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self.info = response_json["data"]
        return self.info

    def get_status(self) -> str:
        """
        Gets the job status.

        Returns:
            The job status, one of "SUCCEEDED", "NOT STARTED", "PENDING", "RUNNING",
            "CANCELLED", "CANCELLING", "FAILED", "ERROR"
        """
        info = self._get_info()
        status = info["status"]
        logger.info(f"Job is {status}")
        return status

    @property
    def is_succeeded(self):
        """Gets True if the job succeeded, False otherwise"""
        return self.get_status() == "SUCCEEDED"

    def track_status(self, report_time: int = 30) -> str:
        """
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
            status = self.get_status()
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
        url = f"{self.auth._endpoint()}/jobs/{self.job_id}/cancel/"
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

    def get_results_json(self, as_dataframe: bool = False) -> Union[Dict, GeoDataFrame]:
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
                Path.cwd() / f"project_{self.auth.project_id}" / f"job_{self.job_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

        download_url = self._get_download_url()
        if unpacking:
            out_filepaths = download_results_from_gcs(
                download_url=download_url, output_directory=output_directory,
            )
        else:
            out_filepaths = download_results_from_gcs_without_unpacking(
                download_url=download_url, output_directory=output_directory,
            )

        self.results = out_filepaths
        return out_filepaths

    def upload_results_to_bucket(
        self, gs_client, bucket, folder, extension: str = ".tgz", version: str = "v0"
    ) -> None:
        """
        Uploads the results of a job directly to a custom google cloud storage bucket.
        """
        download_url = self._get_download_url()
        r = requests.get(download_url)

        if self.order_ids is not None:
            blob = bucket.blob(
                str(Path(version) / Path(folder) / Path(self.order_ids[0] + extension))
            )
            logger.info(
                f"Upload job {self.job_id} results with order_ids to "
                f"{blob.name} ..."
            )
        else:
            blob = bucket.blob(
                str(Path(version) / Path(folder) / Path(self.job_id + extension))
            )
            logger.info(f"Upload job {self.job_id} results to {blob.name} ...")
        blob.upload_from_string(
            data=r.content, content_type="application/octet-stream", client=gs_client,
        )
        logger.info("Uploaded!")

    def map_results(self, show_images=True, name_column: str = "uid") -> None:
        """
        Displays data.json, and if available, one or multiple results geotiffs.

        Args:
            show_images: Shows images if True (default), only features if False.
            name_column: Name of the feature property that provides the Feature/Layer name.
        """
        if self.results is None:
            raise ValueError(
                "You first need to download the results via job.download_results()!"
            )

        def _style_function(feature):  # pylint: disable=unused-argument
            return {
                "fillColor": "#5288c4",
                "color": "blue",
                "weight": 2.5,
                "dashArray": "5, 5",
            }

        def _highlight_function(feature):  # pylint: disable=unused-argument
            return {
                "fillColor": "#ffaf00",
                "color": "red",
                "weight": 3.5,
                "dashArray": "5, 5",
            }

        # Add features to map.
        # Some blocks store vector results in an additional geojson file.
        json_fp = [fp for fp in self.results if fp.endswith(".geojson")]
        if json_fp:
            json_fp = json_fp[0]
        else:
            json_fp = [fp for fp in self.results if fp.endswith(".json")][0]
        df: GeoDataFrame = gpd.read_file(json_fp)

        centroid = box(*df.total_bounds).centroid
        m = folium_base_map(lat=centroid.y, lon=centroid.x,)

        for idx, row in df.iterrows():  # type: ignore
            try:
                feature_name = row.loc[name_column]
            except KeyError:
                feature_name = ""
            layer_name = f"Feature {idx+1} - {feature_name}"
            f = folium.GeoJson(
                row["geometry"],
                name=layer_name,
                style_function=_style_function,
                highlight_function=_highlight_function,
            )
            folium.Popup(
                f"{layer_name}: {row.drop('geometry', axis=0).to_json()}"
            ).add_to(f)
            f.add_to(m)

        # Add image to map.
        plot_file_format = [".tif"]
        raster_filepaths = [
            path for path in self.results if Path(path).suffix in plot_file_format
        ]
        if show_images and raster_filepaths:
            try:
                feature_names = df[name_column].to_list()
            except KeyError:
                feature_names = ""

            for idx, (raster_fp, feature_name) in enumerate(
                zip(raster_filepaths, feature_names)
            ):
                # Folium requires 4326, streaming blocks are 3857
                with rasterio.open(raster_fp) as src:
                    with WarpedVRT(src, crs="EPSG:4326") as vrt:
                        # TODO: Make band configuration available
                        dst_array = vrt.read()[:3, :, :]
                        minx, miny, maxx, maxy = vrt.bounds

                m.add_child(
                    folium.raster_layers.ImageOverlay(
                        np.moveaxis(np.stack(dst_array), 0, 2),
                        bounds=[[miny, minx], [maxy, maxx]],  # different order.
                        name=f"Image {idx+1} - {feature_name}",
                    )
                )

        # Collapse layer control with too many features.
        if df.shape[0] > 4:  # pylint: disable=simplifiable-if-statement  #type: ignore
            collapsed = True
        else:
            collapsed = False
        folium.LayerControl(position="bottomleft", collapsed=collapsed).add_to(m)

        try:
            assert get_ipython() is not None
            display(m)
        except (AssertionError, NameError):
            logger.info(
                "Returning folium map object. To display it directly run in a "
                "Jupyter notebook!"
            )
            return m

    def get_logs(
        self, as_print: bool = True, as_return: bool = False
    ) -> Optional[Dict]:
        """
        Convenience function to print or return the logs of all job tasks.

        Args:
            as_print: Prints the logs, no return.
            as_return: Also returns the log strings.

        Returns:
            The log strings (only if as_return was selected).
        """
        job_logs = {}

        jobtasks: List[Dict] = self.get_jobtasks(return_json=True)  # type: ignore
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
    ) -> Union[List["JobTask"], List[Dict]]:
        """
        Get the individual items of the job as JobTask objects or json.

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
        jobtasks_json: List[Dict] = response_json["data"]

        jobtasks = [
            JobTask(
                auth=self.auth,
                project_id=self.project_id,
                job_id=self.job_id,
                jobtask_id=task["id"],
            )
            for task in jobtasks_json
        ]
        if return_json:
            return jobtasks_json
        else:
            return jobtasks

    def get_jobtasks_results_json(self) -> Dict:
        """
        Convenience function to get the resulting data.json of all job tasks
        in a dictionary of strings.

        Returns:
            The data.json of alle single job tasks.
        """
        jobtasks: List[Dict] = self.get_jobtasks(return_json=True)  # type: ignore
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
