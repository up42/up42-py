import copy
import logging
from typing import Dict, List, Union, Callable
from pathlib import Path
import tempfile
import tarfile

import folium.plugins
import geojson
import geopandas as gpd
import shapely
from shapely.geometry import Point, Polygon
from IPython import get_ipython
from branca.element import CssLink, Element, Figure, JavascriptLink
from geojson import Feature, FeatureCollection
import requests
from tqdm import tqdm

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(name, level=logging.INFO):
    """
    Use level=logging.CRITICAL to disable temporarily.
    """
    logger = logging.getLogger(name)  # pylint: disable=redefined-outer-name
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
    return logger


logger = get_logger(__name__)


def is_notebook() -> bool:
    """Checks if the Python instance is run in a Jupyter notebook."""
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False
    except NameError:
        return False  # Standard Python interpreter


def download_results_from_gcs(
    func_get_download_url: Callable, output_directory: Union[str, Path]
) -> List[str]:
    """
    General download function for results of job and jobtask from cloud storage
    provider.

    Args:
        func_get_download_url:
        output_directory: The file output directory, defaults to the current working
            directory.
    """
    output_directory = Path(output_directory)

    # Download
    tgz_file = tempfile.mktemp()
    with open(tgz_file, "wb") as dst_tgz:
        headers = {"Range": "bytes=0-512"}
        r = requests.get(func_get_download_url(), headers=headers)
        bytes_total = int(r.headers["x-goog-stored-content-length"])
        chunk_size = 10000000  # 10mb
        # TODO: Find better solution for gcs token issue.
        for start in tqdm(range(0, bytes_total, chunk_size)):
            end = start + chunk_size - 1  # Bytes ranges are inclusive
            headers = {"Range": f"bytes={start}-{end}"}
            try:
                r = requests.get(func_get_download_url(), headers=headers)
                r.raise_for_status()
                dst_tgz.write(r.content)
            except requests.exceptions.HTTPError:
                # Tokens expires before download complete.
                r = requests.get(func_get_download_url(), headers=headers)
                dst_tgz.write(r.content)

    # Unpack
    out_filepaths: List[str] = []
    with tarfile.open(tgz_file) as tar:
        members = tar.getmembers()
        files = [
            i for i in members if i.isfile() and str(Path(i.name).name) != "data.json"
        ]
        for file in files:
            f = tar.extractfile(file)
            content = f.read()  # type: ignore
            out_fp = output_directory / f"result_{Path(file.name).name}"
            with open(out_fp, "wb") as dst:
                dst.write(content)
            out_filepaths.append(str(out_fp))

    logger.info("Download successful of %s files %s", len(out_filepaths), out_filepaths)

    return out_filepaths


def folium_base_map(
    lat: float = 52.49190032214706,
    lon: float = 13.39117252959244,
    zoom_start: int = 14,
    width_percent: str = "95%",
    layer_control=False,
) -> folium.Map:
    """Provides a folium map with basic features and UP42 logo."""
    mapfigure = folium.Figure(width=width_percent)
    m = folium.Map(location=[lat, lon], zoom_start=zoom_start, crs="EPSG3857").add_to(
        mapfigure
    )

    tiles = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery"
        "/MapServer/tile/{z}/{y}/{x}.png"
    )
    attr = (
        "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, "
        "AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the "
        "GIS User Community"
    )
    folium.TileLayer(tiles=tiles, attr=attr, name="Satellite - ESRI").add_to(m)

    formatter = "function(num) {return L.Util.formatNum(num, 4) + ' ';};"
    folium.plugins.MousePosition(
        position="bottomright",
        separator=" | ",
        empty_string="NaN",
        lng_first=True,
        num_digits=20,
        prefix="lon/lat:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(m)

    folium.plugins.MiniMap(
        tile_layer="OpenStreetMap", position="bottomright", zoom_level_offset=-6
    ).add_to(m)
    folium.plugins.Fullscreen().add_to(m)
    folium.plugins.FloatImage(
        image="https://cdn-images-1.medium.com/max/140/1*XJ_B7ur_c8bYKniXpKVpWg@2x.png",
        bottom=90,
        left=88,
    ).add_to(m)

    if layer_control:
        folium.LayerControl(position="bottomleft", collapsed=False, zindex=100).add_to(
            m
        )
        # If adding additional layers outside of the folium base map function, don't
        # use this one here. Causes an empty map.
    return m


class DrawFoliumOverride(folium.plugins.Draw):
    def render(self, **kwargs):
        super(DrawFoliumOverride, self).render(**kwargs)

        figure = self.get_root()
        assert isinstance(figure, Figure), (
            "You cannot render this Element " "if it is not in a Figure."
        )

        figure.header.add_child(
            JavascriptLink(
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/"
                "leaflet.draw.js"
            )
        )  # noqa
        figure.header.add_child(
            CssLink(
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/"
                "leaflet.draw.css"
            )
        )  # noqa

        export_style = """
            <style>
                #export {
                    position: absolute;
                    top: 270px;
                    left: 11px;
                    z-index: 999;
                    padding: 6px;
                    border-radius: 3px;
                    box-sizing: border-box;
                    color: #333;
                    background-color: #fff;
                    border: 2px solid rgba(0,0,0,0.5);
                    box-shadow: None;
                    font-family: 'Helvetica Neue';
                    cursor: pointer;
                    font-size: 17px;
                    text-decoration: none;
                    text-align: center;
                    font-weight: bold;
                }
            </style>
        """
        # TODO: How to change hover color?
        export_button = """<a href='#' id='export'>Export as<br/>GeoJson</a>"""
        if self.export:
            figure.header.add_child(Element(export_style), name="export")
            figure.html.add_child(Element(export_button), name="export_button")


def any_vector_to_fc(
    vector: Union[
        Dict, Feature, FeatureCollection, List, gpd.GeoDataFrame, Polygon, Point,
    ],
    as_dataframe: bool = False,
) -> Union[Dict, gpd.GeoDataFrame]:
    """
    Gets a uniform feature collection dictionary (with fc and f bboxes) from any input vector type.

    Args:
        vector: One of Dict, FeatureCollection, Feature, List of bounds coordinates,
            gpd.GeoDataFrame, shapely.geometry.Polygon, shapely.geometry.Point. All assume EPSG 4326
            and Polygons!
        as_dataframe: GeoDataFrame output with as_dataframe=True.
    """
    if not isinstance(
        vector,
        (
            Dict,
            FeatureCollection,
            Feature,
            geojson.Polygon,
            List,
            gpd.GeoDataFrame,
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
    if isinstance(vector, (Dict, FeatureCollection, Feature)):
        try:
            if vector["type"] == "FeatureCollection":
                df = gpd.GeoDataFrame.from_features(vector, crs=4326)
            elif vector["type"] == "Feature":
                df = gpd.GeoDataFrame.from_features(
                    FeatureCollection([vector]), crs=4326
                )
            elif vector["type"] == "Polygon":
                df = gpd.GeoDataFrame.from_features(
                    FeatureCollection([Feature(geometry=vector)]), crs=4326
                )
        except KeyError:
            raise ValueError(
                "Provided geometry dictionary has to include a featurecollection or feature."
            )
    else:
        if isinstance(vector, List):
            if len(vector) == 4:
                box_poly = shapely.geometry.box(*vector)
                df = gpd.GeoDataFrame({"geometry": [box_poly]}, crs=4326)
            else:
                raise ValueError("The list requires 4 bounds coordinates.")
        elif isinstance(vector, Polygon):
            df = gpd.GeoDataFrame({"geometry": [vector]}, crs=4326)
        elif isinstance(vector, Point):
            df = gpd.GeoDataFrame(
                {"geometry": [vector.buffer(0.00001)]}, crs=4326
            )  # Around 1m buffer # TODO: Find better solution than small buffer?
        elif isinstance(vector, gpd.GeoDataFrame):
            df = vector
            if df.crs != "epsg:4326":
                df = df.to_crs(4326)

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
            "geometry_operation needs to be one of bbox", "intersects", "contains",
        )
    try:
        if fc["type"] != "FeatureCollection":
            raise ValueError("Geometry argument only supports Feature Collections!")
    except (KeyError, TypeError):
        raise ValueError("Geometry argument only supports Feature Collections!")

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
            "The provided geometry contains multiple geometries, the %s feature is "
            "taken instead.",
            squash_multiple_features,
        )
        if geometry_operation == "bbox":
            if squash_multiple_features == "union":
                try:
                    query_geometry = list(fc["bbox"])
                except KeyError:
                    query_geometry = list(
                        gpd.GeoDataFrame.from_features(fc, crs=4326).total_bounds
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
                union_poly = gpd.GeoDataFrame.from_features(fc, crs=4326).unary_union
                query_geometry = shapely.geometry.mapping(union_poly)
            elif squash_multiple_features == "first":
                query_geometry = fc["features"][0]["geometry"]
    return query_geometry
