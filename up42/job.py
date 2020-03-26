import logging
import os
import tarfile
import tempfile
from pathlib import Path
from time import sleep
from typing import Dict, List, Union

import folium
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import calculate_default_transform, reproject, Resampling
import requests
import requests.exceptions
from IPython.display import display

from .tools import Tools
from .api import Api
from .jobtask import JobTask
from .utils import get_logger, is_notebook, folium_base_map

logger = get_logger(__name__)  # level=logging.CRITICAL  #INFO


# pylint: disable=dangerous-default-value
class Job(Tools):
    def __init__(
        self, api: Api, project_id: str, job_id: str, order_ids: List[str] = [""],
    ):
        """The Job class provides access to the results, parameters and tasks of UP42
        Jobs (Workflows that have been run as Jobs).

        Public Methods:
            get_status, track_status, cancel_job, download_quicklook, get_result_json
            download_result, upload_result_to_bucket, map_result,
            get_log, get_job_tasks, get_job_tasks_result_json
        """
        self.api = api
        self.project_id = project_id
        self.job_id = job_id
        self.order_ids = order_ids
        if self.api.authenticate:
            self.info = self._get_info()

    def __repr__(self):
        return (
            f"Job(job_id={self.job_id}, project_id={self.project_id}, "
            f"order_ids={str(self.order_ids)}, api={self.api}, info={self.info})"
        )

    def _get_info(self):
        """Gets metadata info from an existing Job"""
        url = f"{self.api._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
        response_json = self.api._request(request_type="GET", url=url)
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

    def track_status(self, report_time: int = 30) -> None:
        """
        Continuously gets the job status until job has finished or failed.

        Args:
            report_time: The intervall (in seconds) when to query the job status.
        """
        status = None
        time_asleep = 0

        logger.info("Tracking job status every %s seconds", report_time)
        while status != "SUCCEEDED":
            logger.setLevel(logging.CRITICAL)
            status = self.get_status()
            logger.setLevel(logging.INFO)

            if time_asleep % report_time == 0:
                logger.info("Job is %s! - %s", status, self.job_id)

            if status in ["NOT STARTED", "PENDING", "RUNNING"]:
                sleep(5)
                time_asleep += 5

            if status == "SUCCEEDED":
                logger.info("Job finished successfully %s - SUCCEEDED!", self.job_id)
                return status

            if status in ["FAILED", "ERROR", "CANCELLED", "CANCELLING"]:
                self.get_log(as_print=True)
                raise ValueError("Job has failed! See the above log.")

    def cancel_job(self) -> None:
        """Cancels a pending or running job."""
        url = f"{self.api._endpoint()}/jobs/{self.job_id}/cancel/"
        self.api._request(request_type="POST", url=url)
        logger.info("Job canceled: %s", self.job_id)

    def download_quicklook(self, out_dir=None) -> Dict:
        """
        Conveniance function that downloads the quicklooks of the first/data jobtask.

        After download, can be plotted via job.plot_quicklook().
        """
        if out_dir is None:
            out_dir = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        # Currently only the first/data task produces quicklooks.
        data_task = self.get_job_tasks()[0]
        out_paths = data_task.download_quicklook(out_dir=out_dir)
        self.quicklook = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths

    def get_result_json(
        self, as_dataframe: bool = False
    ) -> Union[Dict, gpd.GeoDataFrame]:
        """
        Gets the Job result data.json.

        Args:
            as_dataframe: Return type, Default Feature Collection. GeoDataFrame if True.

        Returns:
            The job data.json json.
        """
        url = (
            f"{self.api._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/outputs/data-json/"
        )
        response_json = self.api._request(request_type="GET", url=url)

        if as_dataframe:
            # UP42 results are always in EPSG 4326
            df = gpd.GeoDataFrame.from_features(response_json, crs=4326)
            return df
        else:
            return response_json

    def _get_download_url(self) -> str:
        url = (
            f"{self.api._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/downloads/results/"
        )
        response_json = self.api._request(request_type="GET", url=url)
        download_url = response_json["data"]["url"]
        return download_url

    def download_result(self, out_dir: Union[str, Path] = None,) -> List[str]:
        """
        Downloads and unpacks the job result.

        Args:
            out_dir: The output folder. Default download to the Desktop.

        Returns:
            List of the downloaded results' filepaths.
        """
        # TODO: Overwrite argument
        # TODO: Handle other filetypes than tif, Not working for Fullscenes etc.
        download_url = self._get_download_url()

        if out_dir is None:
            out_dir = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        logger.info("Downloading results of job %s", self.job_id)

        # Download
        tgz_file = tempfile.mktemp()
        with open(tgz_file, "wb") as dst_tgz:
            r = requests.get(download_url)
            dst_tgz.write(r.content)
        # Unpack
        out_filepaths = []
        with tarfile.open(tgz_file) as tar:
            members = tar.getmembers()
            tif_files = [i for i in members if i.isfile() and i.name.endswith(".tif")]
            for idx, tif_file in enumerate(tif_files):
                f = tar.extractfile(tif_file)
                content = f.read()
                # TODO: Maybe jobid_sceneid etc?
                out_fp = out_dir / Path(f"{self.job_id}_{idx}.tif")
                with open(out_fp, "wb") as dst:
                    dst.write(content)
                out_filepaths.append(str(out_fp))

        logger.info(
            "Download successful of %s files %s", len(out_filepaths), out_filepaths
        )
        self.result = out_filepaths  # pylint: disable=attribute-defined-outside-init
        return out_filepaths

    def upload_result_to_bucket(
        self, gs_client, bucket, folder, extension: str = ".tgz", version: str = "v0"
    ) -> None:
        """Uploads the result to a custom google cloud storage bucket."""
        download_url = self._get_download_url()
        r = requests.get(download_url)

        if self.order_ids != [""]:
            blob = bucket.blob(
                str(Path(version) / Path(folder) / Path(self.order_ids[0] + extension))
            )
            logger.info(
                "Upload job %s result with order_ids to %s...", self.job_id, blob.name
            )
        else:
            blob = bucket.blob(
                str(Path(version) / Path(folder) / Path(self.job_id + extension))
            )
            logger.info("Upload job %s result to %s...", self.job_id, blob.name)
        blob.upload_from_string(
            data=r.content, content_type="application/octet-stream", client=gs_client,
        )
        logger.info("Uploaded!")

    def map_result(self, name_column: str = None, info_columns: List = None) -> None:
        """
        Displays data.json, and if available, one or multiple results geotiffs

        name_column: Name of the column that provides the layer name.
        info_columns: Additional columns that are shown when a feature is
            clicked.
        """
        if not is_notebook():
            raise ValueError("Only works in Jupyter notebook.")

        df = self.get_result_json(as_dataframe=True)
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

        for index, row in df.iterrows():
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
                infos = "".join(infos)
                folium.Popup(f"{layer_name}\n{infos}").add_to(f)
            f.add_to(m)
        # Same: folium.GeoJson(df, name=name_column, style_function=style_function,
        # highlight_function=highlight_function).add_to(map)

        # TODO: Not ideal, our streaming images are webmercator, folium requires wgs 84.0
        # TODO: Switch to ipyleaflet!
        # This requires reprojecting on the user pc, not via the api.
        # Reproject raster and add to map
        dst_crs = 4326
        for idx, raster_fp in enumerate(self.result):

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
        if df.shape[0] > 4:  # pylint: disable=simplifiable-if-statement
            collapsed = True
        else:
            collapsed = False
        folium.LayerControl(position="bottomleft", collapsed=collapsed).add_to(m)
        display(m)

    def get_log(self, as_print: bool = True, as_return: bool = False) -> Dict:
        """
        Convenience function to print or return the logs of all job tasks.

        Args:
            as_print: Prints the logs, no return.
            as_return: Also returns the log strings.

        Returns:
            The log strings (only if as_return was selected).
        """
        # TODO: Check if job ended, seems to give error messages when used while still running.
        # but relevant to get logs while running and possible. just sometimes error.

        job_tasks = self.get_job_tasks(return_json=True)
        job_tasks_ids = [task["id"] for task in job_tasks]

        logger.info(
            "Getting logs for %s job tasks: %s", len(job_tasks_ids), job_tasks_ids
        )
        job_logs = {}

        if as_print:
            print(
                f"Printing logs of {len(job_tasks_ids)} JobTasks in Job with job_id "
                f"{self.job_id}:\n"
            )

        for idx, job_task_id in enumerate(job_tasks_ids):
            url = (
                f"{self.api._endpoint()}/projects/{self.project_id}/jobs/"
                f"{self.job_id}/tasks/{job_task_id}/logs"
            )
            response_json = self.api._request(request_type="GET", url=url)

            job_logs[job_task_id] = response_json

            if as_print:
                print("----------------------------------------------------------")
                print(f"JobTask {idx+1} with job_task_id {job_task_id}:\n")
                print(response_json)
            if as_return:
                return job_logs

    def get_job_tasks(self, return_json: bool = False) -> Union["JobTask", Dict]:
        """
        Get the individual items of the job as JobTask objects or json.

        Args:
            return_json: If True returns the json information of the job tasks.

        Returns:
            The job task objects in a list.
        """
        url = (
            f"{self.api._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
            f"/tasks/"
        )
        logger.info("Getting job tasks: %s", self.job_id)
        response_json = self.api._request(request_type="GET", url=url)
        job_tasks_json = response_json["data"]

        job_tasks = [
            JobTask(
                api=self.api,
                project_id=self.project_id,
                job_id=self.job_id,
                job_task_id=task["id"],
            )
            for task in job_tasks_json
        ]
        if return_json:
            return job_tasks_json
        else:
            return job_tasks

    def get_job_tasks_result_json(self) -> Dict:
        """
        Convenience function to get the resulting data.json of all job tasks
        in a dictionary of strings.

        Returns:
            The data.json of alle single job tasks.
        """
        job_tasks = self.get_job_tasks(return_json=True)
        job_tasks_ids = [task["id"] for task in job_tasks]
        job_tasks_results_json = {}
        for job_task_id in job_tasks_ids:
            url = (
                f"{self.api._endpoint()}/projects/{self.project_id}/jobs/{self.job_id}"
                f"/tasks/{job_task_id}/outputs/data-json"
            )
            response_json = self.api._request(request_type="GET", url=url)

            job_tasks_results_json[job_task_id] = response_json
        return job_tasks_results_json
