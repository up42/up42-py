import copy
import logging
from typing import List, Union, Optional
from pathlib import Path
import shutil
import tempfile
import tarfile
import zipfile
import warnings
import functools
from datetime import datetime
from datetime import time as datetime_time

from geopandas import GeoDataFrame
import shapely
from shapely.geometry import Point, Polygon
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
    logger = logging.getLogger(name)  # pylint: disable=redefined-outer-name
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
    function_name: str,
    replacement_name: str,
    version: str = "0.13.0",
    extra_message: str = "",
):
    """
    Decorator for custom deprecation warnings.

    Args:
        function_name: Name of the to be deprecated function.
        replacement_name: Name of the replacement function.
        version: The package version in which the deprecation will happen.
        extra_message: Optional message after default deprecation warning.
    """

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message = (
                f"`{function_name}` will be deprecated in version {version}, "
                f"use `{replacement_name}` instead! {extra_message}"
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return actual_decorator


def download_results_from_gcs(
    download_url: str, output_directory: Union[str, Path]
) -> List[str]:
    """
    General download function for results of job and jobtask from cloud storage
    provider.

    Args:
        download_url: The signed gcs url to download.
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    output_directory = Path(output_directory)

    # Download
    compressed_file = tempfile.mktemp()
    with open(compressed_file, "wb") as dst_tgz:
        try:
            r = requests.get(download_url, stream=True)
            r.raise_for_status()
            for chunk in tqdm(r.iter_content(chunk_size=1024)):
                if chunk:  # filter out keep-alive new chunks
                    dst_tgz.write(chunk)
        except requests.exceptions.HTTPError as err:
            logger.debug(f"Connection error, please try again! {err}")
            raise requests.exceptions.HTTPError(
                f"Connection error, please try again! {err}"
            )

    if tarfile.is_tarfile(compressed_file):
        unpack = tarfile.open
    elif zipfile.is_zipfile(compressed_file):
        unpack = zipfile.ZipFile  # type: ignore
    else:
        raise ValueError("Downloaded file is not a TAR or ZIP archive.")

    with unpack(compressed_file) as f:
        f.extractall(path=output_directory)
        output_folder_path = output_directory / "output"
        out_filepaths = []
        if output_folder_path.exists():
            for src_path in output_folder_path.glob("**/*"):
                dst_path = output_directory / src_path.relative_to(output_folder_path)
                shutil.move(str(src_path), str(dst_path))
                if dst_path.is_dir():
                    out_filepaths += [str(x) for x in dst_path.glob("**/*")]
                elif dst_path.is_file():
                    out_filepaths.append(str(dst_path))
            output_folder_path.rmdir()
        else:
            out_filepaths += [str(x) for x in output_directory.glob("**/*")]

    logger.info(
        f"Download successful of {len(out_filepaths)} files to output_directory "
        f"'{output_directory}': {[Path(p).name for p in out_filepaths]}"
    )
    return out_filepaths


def download_results_from_gcs_without_unpacking(
    download_url: str, output_directory: Union[str, Path]
) -> List[str]:
    """
    General download function for results of job and jobtask from cloud storage
    provider.

    Args:
        download_url: The signed gcs url to download.
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    output_directory = Path(output_directory)

    # Download
    out_filepaths: List[str] = []
    out_fp = Path().joinpath(output_directory, "output.tgz")
    with open(out_fp, "wb") as dst:
        try:
            r = requests.get(download_url, stream=True)
            r.raise_for_status()
            for chunk in tqdm(r.iter_content(chunk_size=1024)):
                if chunk:  # filter out keep-alive new chunks
                    dst.write(chunk)
            out_filepaths.append(str(out_fp))
        except requests.exceptions.HTTPError as err:
            logger.debug(f"Connection error, please try again! {err}")
            raise requests.exceptions.HTTPError(
                f"Connection error, please try again! {err}"
            )

    logger.info(
        f"Download successful of {len(out_filepaths)} files to output_directory"
        f" '{output_directory}': {[Path(p).name for p in out_filepaths]}"
    )
    return out_filepaths


def format_time_period(
    start_date: Optional[Union[str, datetime]], end_date: Optional[Union[str, datetime]]
):
    """
    Formats a time period string from start date and end date.

    Args:
        start_date: Query period starting day as iso-format string or datetime object,
            e.g. "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".
        end_date: Query period ending day as iso-format or datetime object,
            e.g. "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".

    Returns:
        Time period string in the format "2014-01-01T00:00:00Z/2016-12-31T10:11:12Z"
    """
    if start_date is None or end_date is None:
        raise ValueError(
            "When using dates, both start_date and end_date need to be provided."
        )
    # Start and end date can be any combination of str ("YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS")
    # or datetime objects.
    if not isinstance(start_date, datetime):
        start_dt: datetime = datetime.fromisoformat(start_date)
    else:
        start_dt = start_date

    if not isinstance(end_date, datetime):
        end_dt: datetime = datetime.fromisoformat(end_date)
        try:
            # For "YYYY-MM-DD" string the default datetime conversion sets to
            # start of day, but image archive query requires end of day.
            datetime.strptime(end_date, "%Y-%m-%d")  # format validation
            end_dt = datetime.combine(end_dt.date(), datetime_time(23, 59, 59, 999999))
        except ValueError:
            pass
    else:
        end_dt = end_date

    if start_dt > end_dt:
        raise ValueError("The start_date can not be later than the end_date!")

    formatting = "%Y-%m-%dT%H:%M:%S"
    time_period = f"{start_dt.strftime(formatting)}Z/{end_dt.strftime(formatting)}Z"

    return time_period


def any_vector_to_fc(
    vector: Union[
        dict,
        Feature,
        FeatureCollection,
        list,
        GeoDataFrame,
        Polygon,
        Point,
    ],
    as_dataframe: bool = False,
) -> Union[dict, GeoDataFrame]:
    """
    Gets a uniform feature collection dictionary (with fc and f bboxes) from any input vector type.

    Args:
        vector: One of dict, FeatureCollection, Feature, list of bounds coordinates,
            GeoDataFrame, shapely.geometry.Polygon, shapely.geometry.Point.
            All assume EPSG 4326 and Polygons!
        as_dataframe: GeoDataFrame output with as_dataframe=True.
    """
    if not isinstance(
        vector,
        (
            dict,
            FeatureCollection,
            Feature,
            geojson_Polygon,
            list,
            GeoDataFrame,
            Polygon,
            Point,
        ),
    ):
        raise ValueError(
            "The provided geometry muste be a FeatureCollection, Feature, dict, geopandas "
            "Dataframe, shapely Polygon, shapely Point or a list of 4 bounds coordinates."
        )

    ## Transform all possible input geometries to a uniform feature collection.
    vector = copy.deepcopy(vector)  # otherwise changes input geometry.
    if isinstance(vector, (dict, FeatureCollection, Feature)):
        try:
            if vector["type"] == "FeatureCollection":
                df = GeoDataFrame.from_features(vector, crs=4326)
            elif vector["type"] == "Feature":
                # TODO: Handle point features?
                df = GeoDataFrame.from_features(FeatureCollection([vector]), crs=4326)
            elif vector["type"] == "Polygon":  # Geojson geometry
                df = GeoDataFrame.from_features(
                    FeatureCollection([Feature(geometry=vector)]), crs=4326
                )
        except KeyError as e:
            raise ValueError(
                "Provided geometry dictionary has to include a featurecollection or feature."
            ) from e
    else:
        if isinstance(vector, list):
            if len(vector) == 4:
                box_poly = shapely.geometry.box(*vector)
                df = GeoDataFrame({"geometry": [box_poly]}, crs=4326)
            else:
                raise ValueError("The list requires 4 bounds coordinates.")
        elif isinstance(vector, Polygon):
            df = GeoDataFrame({"geometry": [vector]}, crs=4326)
        elif isinstance(vector, Point):
            df = GeoDataFrame(
                {"geometry": [vector.buffer(0.00001)]}, crs=4326
            )  # Around 1m buffer # TODO: Find better solution than small buffer?
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
    try:
        if fc["type"] != "FeatureCollection":
            raise ValueError("Geometry argument only supports Feature Collections!")
    except (KeyError, TypeError) as e:
        raise ValueError("Geometry argument only supports Feature Collections!") from e

    geometry_error = "The provided geometry {}, UP42 only accepts single geometries."
    if len(fc["features"]) != 1:
        logger.info(geometry_error.format("contains multiple geometries"))
        raise ValueError(geometry_error.format("contains multiple geometries"))

    feature = fc["features"][0]
    if feature["geometry"]["type"] == "MultiPolygon":
        logger.info(geometry_error.format("is a MultiPolygon"))
        raise ValueError(geometry_error.format("is a MultiPolygon"))

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
