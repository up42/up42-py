import copy
import dataclasses
import datetime
import functools
import importlib.metadata
import json
import logging
import pathlib
import tarfile
import tempfile
import warnings
import zipfile
from typing import Callable, List, Optional, Union, cast
from urllib import parse

import geojson  # type: ignore
import geopandas  # type: ignore
import pystac_client
import requests
import shapely  # type: ignore
import tqdm
from shapely import geometry  # type: ignore

from up42 import host

TIMEOUT = 120  # seconds
CHUNK_SIZE = 1024


def get_filename(signed_url: str, default_filename: str) -> str:
    """
    Returns the filename from the signed URL
    """
    parsed_url = parse.urlparse(signed_url)
    extension = pathlib.Path(parsed_url.path).suffix
    try:
        file_name = parse.parse_qs(parsed_url.query)["response-content-disposition"][0].split("filename=")[1]
        return f"{file_name}{extension}"
    except (IndexError, KeyError):
        warnings.warn(
            f"Unable to extract filename from URL. Using default filename: {default_filename}",
            UserWarning,
        )
        return f"{default_filename}{extension}"


def get_logger(
    name: str,
    level=logging.INFO,
    verbose: bool = False,
):
    """
    Use level=logging.CRITICAL to disable temporarily.
    """
    inner_logger = logging.getLogger(name)
    inner_logger.setLevel(level)
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
    inner_logger.addHandler(ch)
    inner_logger.propagate = False
    return inner_logger


logger = get_logger(__name__)


def deprecation(
    replacement_name: Optional[str],
    version: str,
):
    """
    Decorator for custom deprecation warnings.

    Args:
        replacement_name: Name of the replacement function.
        version: The breaking package version
        extra_message: Optional message after default deprecation warning.
    """

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            replace_with = f", use `{replacement_name}` instead" if replacement_name else ""
            message = f"`{func.__name__}` is deprecated and will be dropped in version {version}{replace_with}."
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return actual_decorator


def _unpack_tar_files(file_path: str, output_directory: Union[str, pathlib.Path]) -> List[pathlib.Path]:
    out_filepaths: List[pathlib.Path] = []
    if tarfile.is_tarfile(file_path):
        with tarfile.open(file_path) as tar_file:
            for tar_member in tar_file.getmembers():
                if tar_member.isfile():
                    if "output/" in tar_member.name:
                        tar_member.name = tar_member.name.split("output/")[1]
                    tar_file.extract(tar_member, output_directory)
                    out_filepaths.append(pathlib.Path(output_directory) / tar_member.name)
    return out_filepaths


def _unpack_zip_files(file_path: str, output_directory: Union[str, pathlib.Path]) -> List[pathlib.Path]:
    out_filepaths: List[pathlib.Path] = []
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path) as zip_file:
            for zip_info in zip_file.infolist():
                if not zip_info.filename.endswith("/"):
                    if "output/" in zip_info.filename:
                        zip_info.filename = zip_info.filename.split("output/")[1]
                    zip_file.extract(zip_info, output_directory)
                    out_filepaths.append(pathlib.Path(output_directory) / zip_info.filename)
    return out_filepaths


def download_archive(
    download_url: str,
    output_directory: Union[str, pathlib.Path],
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
    with tempfile.NamedTemporaryFile(dir=output_directory) as dst:
        try:
            r = requests.get(download_url, stream=True, timeout=TIMEOUT)
            r.raise_for_status()
            for chunk in tqdm.tqdm(r.iter_content(chunk_size=CHUNK_SIZE)):
                if chunk:  # filter out keep-alive new chunks
                    dst.write(chunk)
            dst.flush()
        except requests.exceptions.HTTPError as err:
            error_message = f"Connection error, please try again! {err}"
            logger.debug(error_message)
            raise requests.exceptions.HTTPError(error_message)
        # Order results are zip, job results are tgz(tar.gzipped)
        out_filepaths = _unpack_tar_files(dst.name, output_directory) + _unpack_zip_files(dst.name, output_directory)

        if not out_filepaths:
            raise UnsupportedArchive("Downloaded file is not a TGZ/TAR or ZIP archive.")
        logger.info(
            "Download successful of %s files to output_directory %s",
            len(out_filepaths),
            output_directory,
        )
    return [str(p) for p in out_filepaths]


class UnsupportedArchive(ValueError):
    pass


def download_file(download_url: str, output_directory: Union[str, pathlib.Path]) -> List[str]:
    """
    General download function for assets, job and jobtasks from cloud storage
    provider.

    Args:
        download_url: The signed gcs url to download.
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    file_name = get_filename(download_url, default_filename="output")
    out_fp = pathlib.Path().joinpath(output_directory, file_name)
    # Download
    with open(out_fp, "wb") as dst:
        try:
            r = requests.get(download_url, stream=True, timeout=TIMEOUT)
            r.raise_for_status()
            for chunk in tqdm.tqdm(r.iter_content(chunk_size=CHUNK_SIZE)):
                if chunk:  # filter out keep-alive new chunks
                    dst.write(chunk)
        except requests.exceptions.HTTPError as err:
            logger.debug("Connection error, please try again! %s", err)
            raise requests.exceptions.HTTPError(f"Connection error, please try again! {err}")

        logger.info("Successfully downloaded the file at %s", out_fp)
        return [str(out_fp)]


def format_time(date: Optional[Union[str, datetime.datetime]], set_end_of_day=False):
    """
    Formats date isostring to datetime string format

    Args:
        date: datetime object or isodatetime string e.g. "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".
        set_end_of_day: Sets the date to end of day, as required for most image archive searches. Only applies for
            type date string without time, e.g. "YYYY-MM-DD", not explicit datetime object or time of day.
    """
    if isinstance(date, str):
        has_time_of_day = len(date) > 11
        date = datetime.datetime.fromisoformat(date)
        if not has_time_of_day and set_end_of_day:
            date = datetime.datetime.combine(date.date(), datetime.time(23, 59, 59, 999999))
    elif isinstance(date, datetime.datetime):
        pass
    else:
        raise ValueError("date needs to be of type datetime or isoformat date string!")

    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def any_vector_to_fc(
    vector: Union[
        geojson.FeatureCollection,
        geojson.Feature,
        dict,
        list,
        geopandas.GeoDataFrame,
        geometry.Polygon,
        geometry.Point,
    ],
    as_dataframe: bool = False,
) -> Union[dict, geopandas.GeoDataFrame]:
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
            geojson.FeatureCollection,
            geojson.Feature,
            dict,
            list,
            geopandas.GeoDataFrame,
            geometry.Polygon,
            geometry.Point,
            geojson.Polygon,
        ),
    ):
        raise ValueError(
            "The provided geometry must be a FeatureCollection, Feature, dict (geojson geometry), geopandas "
            "dataframe, shapely Polygon, Point or a list (bounds coordinates)."
        )

    vector = copy.deepcopy(vector)  # avoid altering input geometry
    if isinstance(vector, (dict, geojson.FeatureCollection, geojson.Feature)):
        try:
            if vector["type"] == "FeatureCollection":
                df = geopandas.GeoDataFrame.from_features(vector, crs=4326)
            elif vector["type"] == "Feature":
                df = geopandas.GeoDataFrame.from_features(geojson.FeatureCollection([vector]), crs=4326)
            else:  # Only geometry dict of Feature
                df = geopandas.GeoDataFrame.from_features(
                    geojson.FeatureCollection([geojson.Feature(geometry=vector)]),
                    crs=4326,
                )
        except KeyError as e:
            raise ValueError("Provided geometry dictionary has to include a FeatureCollection or Feature.") from e
    else:
        if isinstance(vector, list):
            if len(vector) == 4:
                box_poly = shapely.geometry.box(*vector)
                df = geopandas.GeoDataFrame({"geometry": [box_poly]}, crs=4326)
            else:
                raise ValueError("The list requires 4 bounds coordinates.")
        elif isinstance(vector, (geometry.Polygon, geometry.Point)):
            df = geopandas.GeoDataFrame({"geometry": [vector]}, crs=4326)
        elif isinstance(vector, geopandas.GeoDataFrame):
            df = vector
            try:
                if df.crs.to_string() != "EPSG:4326":
                    df = df.to_crs(epsg=4326)
            except AttributeError as e:
                raise AttributeError("GeoDataFrame requires a CRS.") from e

    if as_dataframe:
        return df
    else:
        fc = df.__geo_interface__
        return fc


def validate_fc_up42_requirements(fc: Union[dict, geojson.FeatureCollection]):
    """
    Validate the feature collection if it fits UP42 geometry requirements.
    """
    geometry_error = "UP42 only accepts single geometries, the provided geometry {}."
    if len(fc["features"]) != 1:
        raise ValueError(geometry_error.format("contains multiple geometries"))

    fc_type = fc["features"][0]["geometry"]["type"]
    if fc_type != "Polygon":
        raise ValueError(geometry_error.format(f"is a {fc_type}"))


def fc_to_query_geometry(fc: Union[dict, geojson.FeatureCollection], geometry_operation: str) -> Union[List, dict]:
    """
    From a feature collection with a single feature, depending on the geometry_operation,
    returns the feature as a list of bounds coordinates or a GeoJSON Polygon (as dict).

    Args:
        fc: feature collection
        geometry_operation: One of "bbox", "intersects", "contains".

    Returns:
        The feature as a list of bounds coordinates or a GeoJSON Polygon (as dict)
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


def replace_page_query(url: str, new_page: int) -> str:
    """
    Handle pagination replacement in an encoded url
    Args:
        url (str): a url with query parameters including page
        new_page (int): the desired page starting at 0 to include in the url

    Returns:
        str: the url with the new page parameter.
    """
    parsed_url = parse.urlparse(url)
    query_params = parse.parse_qs(parsed_url.query)
    query_params["page"] = [str(new_page)]

    # Update the query string with the modified parameters
    encoded_query = parse.urlencode(query_params, doseq=True)

    # Reconstruct the modified URL
    return parse.urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            encoded_query,
            parsed_url.fragment,
        )
    )


def get_up42_py_version():
    """Get the version of the up42-py package."""
    return importlib.metadata.version("up42-py")


def read_json(path_or_dict: Union[dict, str, pathlib.Path, None]) -> Optional[dict]:
    if path_or_dict and isinstance(path_or_dict, (str, pathlib.Path)):
        try:
            with open(path_or_dict, encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as ex:
            raise ValueError(f"File {path_or_dict} does not exist!") from ex
    return cast(Optional[dict], path_or_dict)


def stac_client(auth: requests.auth.AuthBase):
    # pystac client accepts both returning and non-returning request modifiers
    # requests.auth.AuthBase is a returning request modifier interface
    request_modifier = cast(Callable[[requests.Request], Optional[requests.Request]], auth)
    return pystac_client.Client.open(
        url=host.endpoint("/v2/assets/stac/"),
        request_modifier=request_modifier,
    )


@dataclasses.dataclass(frozen=True)
class SortingField:
    name: str
    ascending: bool = True

    @property
    def asc(self):
        return SortingField(name=self.name)

    @property
    def desc(self):
        return SortingField(name=self.name, ascending=False)

    def __str__(self):
        order = "asc" if self.ascending else "desc"
        return f"{self.name},{order}"
