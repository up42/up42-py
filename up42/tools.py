"""
SDK conveniance functionality that is made available on the up42 import object (in the init) and is not directly
related to API calls.
"""

import logging
import pathlib
from typing import Dict, Union

import geopandas  # type: ignore
import pandas
import shapely  # type: ignore

from up42 import utils

logger = utils.get_logger(__name__)


def read_vector_file(filename: str = "aoi.geojson", as_dataframe: bool = False) -> Union[Dict, geopandas.GeoDataFrame]:
    """
    Reads vector files (geojson, shapefile, kml, wkt) to a feature collection,
    for use as the AOI geometry in the workflow input parameters
    (see get_input_parameters).

    Example AOI fields are provided, e.g. example/data/aoi_Berlin.geojson

    Args:
        filename: File path of the vector file.
        as_dataframe: Return type, default FeatureCollection, GeoDataFrame if True.

    Returns:
        Feature Collection
    """
    suffix = pathlib.Path(filename).suffix

    if suffix == ".kml":
        # pylint: disable=no-member
        geopandas.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        df = geopandas.read_file(filename, driver="KML")
    elif suffix == ".wkt":
        with open(filename, encoding="utf-8") as wkt_file:
            wkt = wkt_file.read()
            df = pandas.DataFrame({"geometry": [wkt]})
            df["geometry"] = df["geometry"].apply(shapely.wkt.loads)
            df = geopandas.GeoDataFrame(df, geometry="geometry", crs=4326)
    else:
        df = geopandas.read_file(filename)

    if df.crs.to_string() != "EPSG:4326":
        df = df.to_crs(epsg=4326)
    if as_dataframe:
        return df
    else:
        return df.__geo_interface__


def get_example_aoi(location: str = "Berlin", as_dataframe: bool = False) -> Union[Dict, geopandas.GeoDataFrame]:
    """
    Gets predefined, small, rectangular example AOI for the selected location.

    Args:
        location: Location, one of Berlin, Washington.
        as_dataframe: Returns a dataframe instead of dict FeatureColletions
            (default).

    Returns:
        Feature collection JSON with the selected AOI.
    """
    logger.info("Getting small example AOI in location '%s'.", location)
    if location == "Berlin":
        example_aoi = read_vector_file(f"{str(pathlib.Path(__file__).resolve().parent)}/data/aoi_berlin.geojson")
    elif location == "Washington":
        example_aoi = read_vector_file(f"{str(pathlib.Path(__file__).resolve().parent)}/data/aoi_washington.geojson")
    else:
        raise ValueError("Please select one of 'Berlin' or 'Washington' as the location!")

    if as_dataframe:
        df = geopandas.GeoDataFrame.from_features(example_aoi, crs=4326)
        return df
    else:
        return example_aoi


def settings(log: bool = True) -> None:
    """
    Configures settings about logging etc. when using the up42-py package.
    Args:
        log: Activates/deactivates logging, default True is activated logging.
    """
    if log:
        logger.info("Logging enabled (default) - use up42.settings(log=False) to disable.")
    else:
        logger.info("Logging disabled - use up42.settings(log=True) to reactivate.")

    for name in logging.root.manager.loggerDict:
        setattr(logging.getLogger(name), "disabled", not log)
