from pathlib import Path
from typing import Dict, Union, List

import geopandas as gpd
import shapely
from geojson import Feature, FeatureCollection
from shapely.geometry import Point, Polygon
from tqdm import tqdm

from .auth import Auth
from .tools import Tools
from .utils import get_logger, any_vector_to_fc, fc_to_query_geometry

logger = get_logger(__name__)


# TODO: Midterm add catalog results class? Scenes() etc. that also as feedback to workflow input.
# Scenes() would be dataframe with quicklook preview images in it.


blocks_default = [
    "oneatlas-pleiades-fullscene",
    "oneatlas-pleiades-aoiclipped",
    "oneatlas-spot-fullscene",
    "oneatlas-spot-aoiclipped",
    "sobloo-sentinel1-l1c-grd-full",
    "sobloo-sentinel1-l1c-grd-aoiclipped",
    "sobloo-sentinel1-l1c-slc-full",
    "sobloo-sentinel2-lic-msi-full",
    "sobloo-sentinel2-lic-msi-aoiclipped",
    "sobloo-sentinel3-full",
    "sobloo-sentinel5-preview-full",
]
supported_sensors = [
    "pleiades",
    "spot",
    "sentinel1",
    "sentinel2",
    "sentinel3",
    "sentinel5",
]

# pylint: disable=duplicate-code
class Catalog(Tools):
    def __init__(self, auth: Auth, backend: str = "ONE_ATLAS"):
        """The Catalog class enables access to the UP42 catalog search. You can search
        for satellite image scenes for different sensors and criteria like cloud cover etc.

        Public Methods:
            construct_parameters, search, download_quicklooks
        """
        self.auth = auth
        self.querystring = {"backend": backend}
        self.quicklooks = None

    def __repr__(self):
        return f"Catalog(querystring={self.querystring}, auth={self.auth})"

    # pylint: disable=dangerous-default-value
    @staticmethod
    def construct_parameters(
        geometry: Union[
            Dict, Feature, FeatureCollection, List, gpd.GeoDataFrame, Point, Polygon,
        ],
        start_date: str = "2020-01-01",  # TODO: Other format? More time options?
        end_date: str = "2020-01-30",
        sensors: List[str] = [
            "pleiades",
            "spot",
            "sentinel1",
            "sentinel2",
            "sentinel3",
            "sentinel5",
        ],
        limit: int = 1,
        max_cloudcover: float = 100,
        sortby: str = "cloudCoverage",
        ascending: bool = True,
    ) -> Dict:
        """
        Follows STAC principles and property names.

        Args:
            start_date: Query period starting day, format "2020-01-01".
            end_date: Query period ending day, format "2020-01-01".
            geometry:
            limit: The maximum number of search results to return.
            max_cloudcover: Maximum cloudcover % - 100 will return all scenes, 8.4 will return all
                scenes with 8.4 or less cloudcover.
            sortby: The property to sort by, "cloudCoverage", "acquisitionDate",
                "acquisitionIdentifier", "incidenceAngle", "snowCover"
            ascending: Ascending sort order by default, descending if False.

        Returns:
            The constructed parameters dictionary.
        """
        datetime = f"{start_date}T00:00:00Z/{end_date}T00:00:00Z"
        block_filters = []
        for sensor in sensors:
            if sensor not in supported_sensors:
                raise ValueError(
                    f"Currently only these sensors are supported: {supported_sensors}"
                )
            for block in blocks_default:
                if sensor in block.split("-"):
                    block_filters.append(block)
        query_filters = {
            "cloudCoverage": {"lte": max_cloudcover},
            "dataBlock": {"in": block_filters},
        }

        if ascending:
            sort_order = "asc"
        else:
            sort_order = "desc"

        aoi_fc = any_vector_to_fc(vector=geometry,)
        aoi_geometry = fc_to_query_geometry(
            fc=aoi_fc,
            geometry_operation="intersects",
            squash_multiple_features="footprint",
        )

        # TODO: cc also contains nan with sentinel 1 etc. ignore?
        search_paramaters = {
            "datetime": datetime,
            "intersects": aoi_geometry,
            "limit": limit,
            "query": query_filters,
            "sortby": [{"field": f"properties.{sortby}", "direction": sort_order}],
        }

        return search_paramaters

    def search(
        self, search_paramaters: Dict, as_dataframe: bool = True
    ) -> Union[gpd.GeoDataFrame, Dict]:
        """
        Searches the catalog for the the search parameters and returns the metadata of
        the matching scenes.

        Args:
            search_params: The catalog search parameters, see example.
            as_dataframe: return type, GeoDataFrame if True (default), FeatureCollection if False.

        Returns:
            The search results as a GeoDataFrame, optionally as json dict.

        Example:
            ```python
                search_paramaters={
                    "datetime": "2019-01-01T00:00:00Z/2019-01-15T00:00:00Z",
                    "intersects": {
                        "type": "Polygon",
                        "coordinates": [[[13.32113746,52.73971768],[13.15981158,52.2092959],
                        [13.62204483,52.15632025],[13.78859517,52.68655119],[13.32113746,
                        52.73971768]]]},
                    "limit": 1,
                    "sortby": [{"field" : "properties.cloudCoverage","direction" : "asc"}]
                    }
            ```
        """
        logger.info("Searching catalog with: %r", search_paramaters)
        url = f"{self.auth._endpoint()}/catalog/stac/search"
        response_json = self.auth._request(
            "POST", url, search_paramaters, self.querystring
        )
        logger.info("%d results returned.", len(response_json["features"]))
        # UP42 results are always in EPSG 4326
        dst_crs = 4326
        df = gpd.GeoDataFrame.from_features(response_json, crs=dst_crs)
        if df.empty:
            if as_dataframe:
                return df
            else:
                return df.__geo_interface__

        # TODO: Resolve on backend
        # Filter to actual geometries intersecting the aoi (Sobloo search uses a rectangular
        # bounds geometry, can contain scenes that touch the aoi bbox, but not the aoi.
        # So number returned images not consistent with set limit.
        geometry = search_paramaters["intersects"]
        poly = shapely.geometry.shape(geometry)
        df = df[df.intersects(poly)]
        df = df.reset_index()

        # Make scene_id more easily accessible
        def _get_scene_id(row):
            if row["providerName"] == "oneatlas":
                row["scene_id"] = row["providerProperties"]["parentIdentifier"]
            elif row["providerName"] in ["sobloo-radar", "sobloo-image"]:
                row["scene_id"] = row["providerProperties"]["identification"][
                    "externalId"
                ]
            return row

        # pylint: disable=unnecessary-lambda
        df = df.apply(lambda row: _get_scene_id(row), axis=1)
        df.crs = dst_crs  # apply resets crs
        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def download_quicklooks(
        self,
        image_ids: List[str],
        provider: str = "oneatlas",
        output_directory: Union[str, Path, None] = None,
    ) -> List[str]:
        """
        Gets the quicklooks of scenes, from oneatlas or sobloo.

        After download, can be plotted via catalog.plot_quicklooks().
        Args:
            image_ids: provider image_id in the form "6dffb8be-c2ab-46e3-9c1c-6958a54e4527"
            provider:  One of "oneatlas", "sobloo"
            output_directory: The file output directory, defaults to the current working
                directory.

        Returns:
            List of quicklook image output file paths.
        """
        logger.info("Getting quicklooks for image_ids %s", image_ids)

        if output_directory is None:
            output_directory = (
                Path.cwd() / f"project_{self.auth.project_id}" / "catalog"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Download directory: %s", str(output_directory))

        if isinstance(image_ids, str):
            image_ids = [image_ids]

        out_paths: List[str] = []
        for image_id in tqdm(image_ids):
            out_path = output_directory / f"quicklook_{image_id}.jpg"
            out_paths.append(str(out_path))

            url = (
                f"{self.auth._endpoint()}/catalog/{provider}/image/{image_id}/quicklook"
            )
            response = self.auth._request(
                request_type="GET", url=url, return_text=False
            )

            with open(out_path, "wb") as dst:
                for chunk in response:
                    dst.write(chunk)

        self.quicklooks = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths
