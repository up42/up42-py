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
from typing import Any, Callable, List, Optional, Union, cast
from urllib import parse

import geojson  # type: ignore
import pystac_client
import requests
import tqdm

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
    """

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            replace_with = f" Use `{replacement_name}` instead." if replacement_name else ""
            message = f"`{func.__name__}` is deprecated and will be removed in version {version}{replace_with}."
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


@dataclasses.dataclass
class ImageFile:
    url: str
    file_name: str = "output"
    session: requests.Session = dataclasses.field(default=requests.session(), repr=False, compare=False)

    def download(self, output_directory: Union[str, pathlib.Path]) -> pathlib.Path:
        file_name = get_filename(self.url, default_filename=self.file_name)
        path = pathlib.Path().joinpath(output_directory, file_name)
        with open(path, "wb") as dst:
            try:
                r = self.session.get(self.url, stream=True, timeout=TIMEOUT)
                r.raise_for_status()
                for chunk in tqdm.tqdm(r.iter_content(chunk_size=CHUNK_SIZE)):
                    if chunk:  # filter out keep-alive new chunks
                        dst.write(chunk)
            except requests.exceptions.HTTPError as err:
                logger.debug("Connection error, please try again! %s", err)
                raise requests.exceptions.HTTPError(f"Connection error, please try again! {err}")

            logger.info("Successfully downloaded the file at %s", path)
            return path


def download_file(download_url: str, output_directory: Union[str, pathlib.Path]) -> List[str]:
    """
    General download function for assets, job and jobtasks from cloud storage
    provider.

    Args:
        download_url: The signed gcs url to download.
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    image = ImageFile(download_url)
    return [str(image.download(output_directory))]


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


def paged_query(params: dict[str, Any], endpoint: str, session: requests.Session):
    params = {key: value for key, value in params.items() if value is not None}
    params["page"] = 0

    def get_pages():
        while True:
            response = session.get(host.endpoint(endpoint), params=params).json()
            yield response["content"]
            params["page"] += 1
            if params["page"] >= response["totalPages"]:
                break

    return (entry for page in get_pages() for entry in page)
