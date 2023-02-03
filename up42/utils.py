import copy
import logging
from typing import List, Union, Optional
from pathlib import Path
import tempfile
import tarfile
import zipfile
import warnings
from datetime import datetime
from datetime import time as datetime_time
from functools import wraps

from geopandas import GeoDataFrame
import shapely
from shapely.geometry import Polygon, Point
from geojson import Feature, FeatureCollection
from geojson import Polygon as geojson_Polygon
import requests
from tqdm import tqdm


def get_logger(
    name: str,
    level=logging.INFO,
    verbose: bool = False,
):
    """
    Use level=logging.CRITICAL to disable temporarily.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if verbose:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)"
    else:
        # hide logger module & level, truncate log messages > 2000 characters (e.g. huge geometries)
        log_format = "%(asctime)s - %(message).2000s"
    formatter = logging.Formatter(log_format)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
    return logger


logger = get_logger(__name__)


def deprecation(
    replacement_name: str,
    version: str,
    extra_message: str = "",
):
    """
    Decorator for custom deprecation warnings.

    Args:
        replacement_name: Name of the replacement function.
        version: The package version in which the deprecation will happen.
        extra_message: Optional message after default deprecation warning.
    """

    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = (
                f"`{func.__name__}` will be deprecated in version {version}, "
                f"use `{replacement_name}` instead! {extra_message}"
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return actual_decorator


def download_from_gcs_unpack(
    download_url: str,
    output_directory: Union[str, Path],
) -> List[str]:
    """
    General download function for results of storage assets, job & jobtask from cloud storage
    provider.

    Args:
        download_url: The signed gcs url to download.
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    # Download
    out_temp = tempfile.mkstemp()[1]
    with open(out_temp, "wb") as dst:
        try:
            r = requests.get(download_url, stream=True)
            r.raise_for_status()
            for chunk in tqdm(r.iter_content(chunk_size=1024)):
                if chunk:  # filter out keep-alive new chunks
                    dst.write(chunk)
        except requests.exceptions.HTTPError as err:
            error_message = f"Connection error, please try again! {err}"
            logger.debug(error_message)
            raise requests.exceptions.HTTPError(error_message)

    # Unpack
    # Order results are zip, job results are tgz(tar.gzipped)
    out_filepaths: List[Path] = []
    if tarfile.is_tarfile(out_temp):
        with tarfile.open(out_temp) as tar_file:
            for tar_member in tar_file.getmembers():
                if tar_member.isfile():
                    # Avoid up42 inherent output/ .. directory
                    if "output/" in tar_member.name:
                        tar_member.name = tar_member.name.split("output/")[1]
                    tar_file.extract(tar_member, output_directory)
                    out_filepaths.append(Path(output_directory) / tar_member.name)
    elif zipfile.is_zipfile(out_temp):
        with zipfile.ZipFile(out_temp) as zip_file:
            for zip_info in zip_file.infolist():
                if not zip_info.filename.endswith("/"):
                    # Avoid up42 inherent output/ .. directory
                    if "output/" in zip_info.filename:
                        zip_info.filename = zip_info.filename.split("output/")[1]
                    zip_file.extract(zip_info, output_directory)
                    out_filepaths.append(Path(output_directory) / zip_info.filename)
    else:
        raise ValueError("Downloaded file is not a TGZ/TAR or ZIP archive.")

    logger.info(
        f"Download successful of {len(out_filepaths)} files to output_directory "
        f"'{output_directory}': {[p.name for p in out_filepaths]}"
    )
    out_filepaths = [str(p) for p in out_filepaths]  # type: ignore
    return out_filepaths  # type: ignore


def download_gcs_not_unpack(
    download_url: str, output_directory: Union[str, Path]
) -> List[str]:
    """
    General download function for assets, job and jobtasks from cloud storage
    provider.

    Args:
        download_url: The signed gcs url to download.
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    if ".tgz" in download_url:
        file_ending = "tgz"
    elif ".zip" in download_url:
        file_ending = "zip"
    else:
        ValueError("To be downloaded file is not a TGZ/TAR or ZIP archive.")
    out_fp = Path().joinpath(output_directory, f"output.{file_ending}")

    # Download
    with open(out_fp, "wb") as dst:
        try:
            r = requests.get(download_url, stream=True)
            r.raise_for_status()
            for chunk in tqdm(r.iter_content(chunk_size=1024)):
                if chunk:  # filter out keep-alive new chunks
                    dst.write(chunk)
        except requests.exceptions.HTTPError as err:
            logger.debug(f"Connection error, please try again! {err}")
            raise requests.exceptions.HTTPError(
                f"Connection error, please try again! {err}"
            )

    logger.info(
        f"Download successful of original archive file to output_directory"
        f" '{output_directory}': {out_fp.name}. To automatically unpack the archive use `unpacking=True`"
    )
    out_filepaths = [str(out_fp)]
    return out_filepaths


def format_time(date: Optional[Union[str, datetime]], set_end_of_day=False):
    """
    Formats date isostring to datetime string format

    Args:
        date: datetime object or isodatetime string e.g. "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".
        set_end_of_day: Sets the date to end of day, as required for most image archive searches. Only applies for
            type date string without time, e.g. "YYYY-MM-DD", not explicit datetime object or time of day.
    """
    if isinstance(date, str):
        has_time_of_day = len(date) > 11
        date = datetime.fromisoformat(date)  # type: ignore
        if not has_time_of_day and set_end_of_day:
            date = datetime.combine(date.date(), datetime_time(23, 59, 59, 999999))
    elif isinstance(date, datetime):
        pass
    else:
        raise ValueError("date needs to be of type datetime or isoformat date string!")

    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def any_vector_to_fc(
    vector: Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point],
    as_dataframe: bool = False,
) -> Union[dict, GeoDataFrame]:
    """
    Gets a uniform feature collection dictionary (with fc and f bboxes) from any input vector type.

    Args:
        vector: One of FeatureCollection, Feature, dict (geojson geometry), list (bounds coordinates),
            GeoDataFrame, shapely.Polygon, shapely.Point. All assume EPSG 4326!
        as_dataframe: GeoDataFrame output with as_dataframe=True.
    """
    if not isinstance(
        vector,
        (
            FeatureCollection,
            Feature,
            dict,
            list,
            GeoDataFrame,
            Polygon,
            Point,
            geojson_Polygon,
        ),
    ):
        raise ValueError(
            "The provided geometry must be a FeatureCollection, Feature, dict (geojson geometry), geopandas "
            "dataframe, shapely Polygon, Point or a list (bounds coordinates)."
        )

    vector = copy.deepcopy(vector)  # avoid altering input geometry
    if isinstance(vector, (dict, FeatureCollection, Feature)):
        try:
            if vector["type"] == "FeatureCollection":
                df = GeoDataFrame.from_features(vector, crs=4326)
            elif vector["type"] == "Feature":
                df = GeoDataFrame.from_features(FeatureCollection([vector]), crs=4326)
            else:  # Only geometry dict of Feature
                df = GeoDataFrame.from_features(
                    FeatureCollection([Feature(geometry=vector)]), crs=4326
                )
        except KeyError as e:
            raise ValueError(
                "Provided geometry dictionary has to include a FeatureCollection or Feature."
            ) from e
    else:
        if isinstance(vector, list):
            if len(vector) == 4:
                box_poly = shapely.geometry.box(*vector)
                df = GeoDataFrame({"geometry": [box_poly]}, crs=4326)
            else:
                raise ValueError("The list requires 4 bounds coordinates.")
        elif isinstance(vector, (Polygon, Point)):
            df = GeoDataFrame({"geometry": [vector]}, crs=4326)
        elif isinstance(vector, GeoDataFrame):
            df = vector
            try:
                if df.crs.to_string() != "EPSG:4326":
                    df = df.to_crs(epsg=4326)
            except AttributeError as e:
                raise AttributeError("GeoDataFrame requires a crs.") from e

    if as_dataframe:
        return df
    else:
        fc = df.__geo_interface__
        return fc


def validate_fc_up42_requirements(fc: Union[dict, FeatureCollection]):
    """
    Validate the feature collection if it fits UP42 geometry requirements.
    """
    geometry_error = "UP42 only accepts single geometries, the provided geometry {}."
    if len(fc["features"]) != 1:
        logger.info(geometry_error.format("contains multiple geometries"))
        raise ValueError(geometry_error.format("contains multiple geometries"))

    fc_type = fc["features"][0]["geometry"]["type"]
    if fc_type != "Polygon":
        logger.info(geometry_error.format(f"is a {fc_type}"))
        raise ValueError(geometry_error.format(f"is a {fc_type}"))


def fc_to_query_geometry(
    fc: Union[dict, FeatureCollection], geometry_operation: str
) -> Union[List, dict]:
    """
    From a feature collection with a single feature, depending on the geometry_operation,
    returns the feature as a list of bounds coordinates or a geojson Polygon (as dict).

    Args:
        fc: feature collection
        geometry_operation: One of "bbox", "intersects", "contains".

    Returns:
        The feature as a list of bounds coordinates or a geojson Polygon (as dict)
    """
    validate_fc_up42_requirements(fc)
    feature = fc["features"][0]

    if geometry_operation == "bbox":
        try:
            query_geometry = list(feature["bbox"])
        except KeyError:
            query_geometry = list(shapely.geometry.shape(feature["geometry"]).bounds)
    elif geometry_operation in ["intersects", "contains"]:
        query_geometry = feature["geometry"]
    else:
        raise ValueError(
            "geometry_operation needs to be one of bbox, intersects or contains!",
        )

    return query_geometry


def filter_jobs_on_mode(
    jobs_json: List[dict], test_jobs: bool = True, real_jobs: bool = True
) -> List[dict]:
    """
    Filter jobs according to selected mode.

    Args:
        jobs_json: List of jobs as returned by /jobs endpoint.
        test_jobs: If returning test jobs or test queries.
        real_jobs: If returning real jobs.

    Returns:
        List of filtered jobs.

    Raises:
        ValueError: When no modes are selected to filter jobs with.
    """
    selected_modes = []
    if test_jobs:
        selected_modes.append("DRY_RUN")
    if real_jobs:
        selected_modes.append("DEFAULT")
    if not selected_modes:
        raise ValueError("At least one of test_jobs and real_jobs must be True.")
    jobs_json = [job for job in jobs_json if job["mode"] in selected_modes]
    logger.info(f"Returning {selected_modes} jobs.")
    return jobs_json


def autocomplete_order_parameters(order_parameters: dict, schema: dict):
    """
    Adds missing required catalog/tasking order parameters and logs parameter suggestions.

    Args:
        order_parameters: The initial order_parameters, in format
            {"dataProduct": data_product_id, "params" : {...}}
        schema: The data product parameter schema from .get_data_product_schema
        The existing order parameter params

    Returns:
        The order parameters with complete params
    """
    additional_params = {
        param: None
        for param in schema["required"]
        if param not in order_parameters["params"]
    }
    order_parameters["params"] = dict(order_parameters["params"], **additional_params)

    # Log message help for parameter selection
    for param in additional_params.keys():
        if param in ["aoi", "geometry"]:
            continue
        elif "allOf" in schema["properties"][param]:  # has further definitions key
            potential_values = [x["id"] for x in schema["definitions"][param]["enum"]]
            logger.info(f"As `{param}` select one of {potential_values}")
        else:
            # Full information for simple parameters
            del schema["properties"][param]["title"]
            logger.info(f"As `{param}` select `{schema['properties'][param]}`")
    return order_parameters
