import logging
from pathlib import Path
from time import sleep
from typing import Dict, List, Union

import folium
import geopandas as gpd
import numpy as np
import rasterio
import requests
import requests.exceptions
from IPython.display import display
from rasterio.io import MemoryFile
from rasterio.warp import calculate_default_transform, reproject, Resampling

from .auth import Auth
from .jobtask import JobTask
from .tools import Tools
from .utils import get_logger, is_notebook, folium_base_map, download_results_from_gcs

logger = get_logger(__name__)


# pylint: disable=duplicate-code
class Job(Tools):
    def __init__(
        self, auth: Auth, project_id: str, job_id: str, order_ids: List[str] = None,
    ):
        """The Job class provides access to the results, parameters and tasks of UP42
        Jobs (Workflows that have been run as Jobs).

        Public Methods:
            get_status, track_status, cancel_job, download_quicklooks, get_results_json
            download_results, upload_results_to_bucket, map_results,
            get_logs, get_jobtasks, get_jobtasks_results_json
        """
        self.auth = auth
        self.project_id = project_id
        self.job_id = job_id
        self.quicklooks = None
        self.results = None
        if order_ids is None:
            self.order_ids = [""]
        if self.auth.get_info:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"Job(job_id={self.job_id}, project_id={self.project_id}, "
            f"order_ids={str(self.order_ids)}, auth={self.auth}, info={self.info})"
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
            The job status.
        """
        # logger.info("Getting job status: %s", self.job_id)
        info = self._get_info()
        status = info["status"]
        logger.info("Job is %s", status)
        return status

    def track_status(self, report_time: int = 30) -> str:
        """
        Continuously gets the job status until job has finished or failed.

        Internally checks every five seconds for the status, prints the log every
        time interval given in report_time argument.

        Args:
            report_time: The intervall (in seconds) when to query the job status.
        """
        logger.info(
            "Tracking job status continuously, reporting every %s seconds...",
            report_time,
        )
        status = "NOT STARTED"
        time_asleep = 0

        while status != "SUCCEEDED":
            logger.setLevel(logging.CRITICAL)
            status = self.get_status()
            logger.setLevel(logging.INFO)

            if status in ["NOT STARTED", "PENDING", "RUNNING"]:
                if time_asleep != 0 and time_asleep % report_time == 0:
                    logger.info("Job is %s! - %s", status, self.job_id)
            elif status in ["FAILED", "ERROR"]:
                logger.info("Job is %s! - %s - Printing logs ...", status, self.job_id)
                self.get_logs(as_print=True)
                raise ValueError("Job has failed! See the above log.")
            elif status in ["CANCELLED", "CANCELLING"]:
                logger.info("Job is %s! - %s", status, self.job_id)
                raise ValueError("Job has been cancelled!")
            elif status == "SUCCEEDED":
                logger.info("Job finished successfully! - %s", self.job_id)

            sleep(5)
            time_asleep += 5

        return status

    def cancel_job(self) -> None:
        """Cancels a pending or running job."""
        url = f"{self.auth._endpoint()}/jobs/{self.job_id}/cancel/"
        self.auth._request(request_type="POST", url=url)
        logger.info("Job canceled: %s", self.job_id)

    def download_quicklooks(
        self, output_directory: Union[str, Path, None] = None
    ) -> List[str]:
        """
        Conveniance function that downloads the quicklooks of the data (dirst) jobtask.

        After download, can be plotted via job.plot_quicklooks().
        """
        # Currently only the first/data task produces quicklooks.
        data_task = self.get_jobtasks()[0]
        out_paths: List[str] = data_task.download_quicklooks(  # type: ignore
            output_directory=output_directory
        )  # type: ignore
        self.quicklooks = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths

    def get_results_json(
        self, as_dataframe: bool = False
    ) -> Union[Dict, gpd.GeoDataFrame]:
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

        if as_dataframe:
            # UP42 results are always in EPSG 4326
            df = gpd.GeoDataFrame.from_features(response_json, crs=4326)
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
        self, output_directory: Union[str, Path, None] = None,
    ) -> List[str]:
        """
        Downloads and unpacks the job results.

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.

        Returns:
            List of the downloaded results' filepaths.
        """
        # TODO: Overwrite argument
        logger.info("Downloading results of job %s", self.job_id)

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

    def upload_results_to_bucket(
        self, gs_client, bucket, folder, extension: str = ".tgz", version: str = "v0"
    ) -> None:
        """Uploads the results to a custom google cloud storage bucket."""
        download_url = self._get_download_url()
        r = requests.get(download_url)

        if self.order_ids != [""]:
            blob = bucket.blob(
                str(Path(version) / Path(folder) / Path(self.order_ids[0] + extension))
            )
            logger.info(
                "Upload job %s results with order_ids to %s...", self.job_id, blob.name
            )
        else:
            blob = bucket.blob(
                str(Path(version) / Path(folder) / Path(self.job_id + extension))
            )
            logger.info("Upload job %s results to %s...", self.job_id, blob.name)
        blob.upload_from_string(
            data=r.content, content_type="application/octet-stream", client=gs_client,
        )
        logger.info("Uploaded!")

    def map_results(self, name_column: str = None, info_columns: List = None) -> None:
        """
        Displays data.json, and if available, one or multiple results geotiffs

        name_column: Name of the column that provides the layer name.
        info_columns: Additional columns that are shown when a feature is
            clicked.
        """
        if not is_notebook():
            raise ValueError("Only works in Jupyter notebook.")

        df: gpd.GeoDataFrame = self.get_results_json(as_dataframe=True)  # type: ignore
        # TODO: centroid of total_bounds
        centroid = df.iloc[0].geometry.centroid

        m = folium_base_map(lat=centroid.y, lon=centroid.x,)

        # Add features from data.json.
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

        for index, row in df.iterrows():  # type: ignore
            try:
                layer_name = row[name_column]
            except KeyError:
                layer_name = f"Layer {index+1}"

            f = folium.GeoJson(
                row["geometry"],
                name=layer_name,  # ('{}{}'.format(row['dep'], row['dest'])),
                style_function=_style_function,
                highlight_function=_highlight_function,
            )

            if not info_columns:
                folium.Popup(f"{layer_name}").add_to(f)
            else:
                if not isinstance(info_columns, list):
                    raise ValueError("Provide a list!")
                infos = [f"{row[info_col]}\n" for info_col in info_columns]
                infos = "".join(infos)  # type: ignore
                folium.Popup(f"{layer_name}\n{infos}").add_to(f)
            f.add_to(m)
        # Same: folium.GeoJson(df, name=name_column, style_function=style_function,
        # highlight_function=highlight_function).add_to(map)

        # TODO: Not ideal, our streaming images are webmercator, folium requires wgs 84.0
        # TODO: Switch to ipyleaflet!
        # This requires reprojecting on the user pc, not via the api.
        # Reproject raster and add to map
        dst_crs = 4326
        results: List[Path] = self.results
        for idx, raster_fp in enumerate(results):

            with rasterio.open(raster_fp) as src:
                dst_profile = src.meta.copy()
                if src.crs != dst_crs:
                    transform, width, height = calculate_default_transform(
                        src.crs, dst_crs, src.width, src.height, *src.bounds
                    )
                    dst_profile.update(
                        {
                            "crs": dst_crs,
                            "transform": transform,
                            "width": width,
                            "height": height,
                        }
                    )

                    with MemoryFile() as memfile:
                        with memfile.open(**dst_profile) as mem:
                            for i in range(1, src.count + 1):
                                reproject(
                                    source=rasterio.band(src, i),
                                    destination=rasterio.band(mem, i),
                                    src_transform=src.transform,
                                    src_crs=src.crs,
                                    dst_transform=transform,
                                    dst_crs=dst_crs,
                                    resampling=Resampling.nearest,
                                )

                            # TODO: What if more bands than 3-4?
                            dst_array = mem.read()
                            minx, miny, maxx, maxy = mem.bounds

            dst_array = np.moveaxis(np.stack(dst_array), 0, 2)
            m.add_child(
                folium.raster_layers.ImageOverlay(
                    dst_array,
                    bounds=[[miny, minx], [maxy, maxx]],  # andere reihenfolge.
                    name=f"Image - {idx} - {raster_fp}",
                )
            )

        # Collapse layer control with too many features.
        if df.shape[0] > 4:  # pylint: disable=simplifiable-if-statement  #type: ignore
            collapsed = True
        else:
            collapsed = False
        folium.LayerControl(position="bottomleft", collapsed=collapsed).add_to(m)
        display(m)

    def get_logs(self, as_print: bool = True, as_return: bool = False):
        """
        Convenience function to print or return the logs of all job tasks.

        Args:
            as_print: Prints the logs, no return.
            as_return: Also returns the log strings.

        Returns:
            The log strings (only if as_return was selected).
        """
        jobtasks: List[Dict] = self.get_jobtasks(return_json=True)  # type: ignore
        jobtasks_ids = [task["id"] for task in jobtasks]

        logger.info(
            "Getting logs for %s job tasks: %s", len(jobtasks_ids), jobtasks_ids
        )
        job_logs = {}

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
        logger.info("Getting job tasks: %s", self.job_id)
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
