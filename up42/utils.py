import copy
import logging
from typing import Dict, List, Union
from pathlib import Path
import shutil
import tempfile
import tarfile
import zipfile
import warnings
import functools

from geopandas import GeoDataFrame
import shapely
from shapely.geometry import Point, Polygon
from geojson import Feature, FeatureCollection
from geojson import Polygon as geojson_Polygon
import requests
from tqdm import tqdm


def get_logger(
    name,
    level=logging.INFO,
    verbose=False,
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
            r = requests.get(download_url)
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
            r = requests.get(download_url)
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


def any_vector_to_fc(
    vector: Union[
        Dict,
        Feature,
        FeatureCollection,
        List,
        GeoDataFrame,
        Polygon,
        Point,
    ],
    as_dataframe: bool = False,
) -> Union[Dict, GeoDataFrame]:
    """
    Gets a uniform feature collection dictionary (with fc and f bboxes) from any input vector type.

    Args:
        vector: One of Dict, FeatureCollection, Feature, List of bounds coordinates,
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
            "The provided geometry muste be a FeatureCollection, Feature, Dict, geopandas "
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
    fc: Union[Dict, FeatureCollection],
    geometry_operation: str,
    squash_multiple_features: str = "union",
) -> Union[List, dict]:
    """
    From a feature collection (one or multiple polygons) & any geometry_operation,
    gets a single query geometry for the workflow parameters.
    Returns either a list of bounds or a geojson Polygon (as dict) depending on geometry_operation.
    If an input fc with multiple features is provided, it gets squashed to a single
    output geometry, either by taking the first geometry or the union (footprint) of all geometries,
    depending on handle_multiple_features.

    Examples (geometry & geometry_operation > always returns a single feature):
        Single input geometries:
            - feature & "intersects/contains" > same as input feature
            - feature & "bbox" > rectangular feature that is the bbox of the input feature
        Multiple input geometries:
            - features & "intersects/contains" > feature of first object in fc or union
                of fc (depending on "handle_multiple_features")
            - features & "bbox" > rectangular feature of first object in fc or union of
                fc (depending on "handle_multiple_features")

    Args:
        fc: feature collection
        geometry_operation: One of "bbox", "intersects", "contains".
        squash_multiple_features: One of "union" (default, footprint of all features)
            or "first" (takes the first feature.

    Returns:

    """
    if geometry_operation not in ["bbox", "intersects", "contains"]:
        raise ValueError(
            "geometry_operation needs to be one of bbox",
            "intersects",
            "contains",
        )
    try:
        if fc["type"] != "FeatureCollection":
            raise ValueError("Geometry argument only supports Feature Collections!")
    except (KeyError, TypeError) as e:
        raise ValueError("Geometry argument only supports Feature Collections!") from e

    # TODO: Handle multipolygons

    # With the now uniform feature collection, decide to return a feature or list of bounds (bbox).
    if len(fc["features"]) == 1:
        f = fc["features"][0]
        if geometry_operation == "bbox":
            try:
                query_geometry = list(f["bbox"])
            except KeyError:
                query_geometry = list(shapely.geometry.shape(f["geometry"]).bounds)
        elif geometry_operation in ["intersects", "contains"]:
            query_geometry = f["geometry"]
    # In case of multiple geometries transform the feature collection a single aoi
    # geometry via handle_multiple_features method.
    else:
        logger.info(
            f"The provided geometry contains multiple geometries, "
            f"the {squash_multiple_features} feature is taken instead."
        )
        if geometry_operation == "bbox":
            if squash_multiple_features == "union":
                try:
                    query_geometry = list(fc["bbox"])
                except KeyError:
                    query_geometry = list(
                        GeoDataFrame.from_features(fc, crs=4326).total_bounds
                    )
            elif squash_multiple_features == "first":
                try:
                    query_geometry = fc["features"][0]["bbox"]
                except KeyError:
                    query_geometry = list(
                        shapely.geometry.shape(fc["features"][0]["geometry"]).bounds
                    )
        elif geometry_operation in [
            "intersects",
            "contains",
        ]:  # pylint: disable=no-else-raise
            if squash_multiple_features == "union":
                union_poly = GeoDataFrame.from_features(fc, crs=4326).unary_union
                query_geometry = shapely.geometry.mapping(union_poly)
            elif squash_multiple_features == "first":
                query_geometry = fc["features"][0]["geometry"]
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
