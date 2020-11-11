"""
Catalog search functionality
"""

from pathlib import Path
from typing import Dict, Union, List

from geopandas import GeoDataFrame
from shapely.geometry import shape
from shapely.geometry import Point, Polygon
from geojson import Feature, FeatureCollection
from tqdm import tqdm

from up42.auth import Auth
from up42.tools import Tools
from up42.viztools import VizTools
from up42.utils import get_logger, any_vector_to_fc, fc_to_query_geometry

logger = get_logger(__name__)


supported_sensors = {
    "pleiades": {
        "blocks": [
            "oneatlas-pleiades-fullscene",
            "oneatlas-pleiades-aoiclipped",
        ],
        "provider": "oneatlas",
    },
    "spot": {
        "blocks": [
            "oneatlas-spot-fullscene",
            "oneatlas-spot-aoiclipped",
        ],
        "provider": "oneatlas",
    },
    "sentinel1": {
        "blocks": [
            "sobloo-s1-grd-fullscene",
            "sobloo-s1-grd-aoiclipped",
            "sobloo-s1-slc-fullscene",
        ],
        "provider": "sobloo-image",
    },
    "sentinel2": {
        "blocks": [
            "sobloo-s2-l1c-fullscene",
            "sobloo-s2-l1c-aoiclipped",
        ],
        "provider": "sobloo-image",
    },
    "sentinel3": {"blocks": ["sobloo-s3"], "provider": "sobloo-image"},
    "sentinel5p": {
        "blocks": [
            "sobloo-s5p",
        ],
        "provider": "sobloo-image",
    },
}

# pylint: disable=duplicate-code
class Catalog(VizTools, Tools):
    def __init__(self, auth: Auth):
        """
        The Catalog class enables access to the UP42 catalog search. You can search
        for satellite image scenes (for different sensors and criteria like cloud cover),
        plot the scene coverage and download and plot the scene quicklooks.
        """
        self.auth = auth
        self.quicklooks = None

    def __repr__(self):
        return f"Catalog(auth={self.auth})"

    # pylint: disable=dangerous-default-value
    @staticmethod
    def construct_parameters(
        geometry: Union[
            Dict,
            Feature,
            FeatureCollection,
            List,
            GeoDataFrame,
            Point,
            Polygon,
        ],
        start_date: str = "2020-01-01",
        end_date: str = "2020-01-30",
        sensors: List[str] = [
            "pleiades",
            "spot",
            "sentinel1",
            "sentinel2",
            "sentinel3",
            "sentinel5p",
        ],
        limit: int = 10,
        max_cloudcover: float = 100,
        sortby: str = "acquisitionDate",
        ascending: bool = True,
    ) -> Dict:
        """
        Follows STAC principles and property names.

        Args:
            geometry: The search geometry, one of Dict, Feature, FeatureCollection,
                List, GeoDataFrame, Point, Polygon.
            start_date: Query period starting day, format "2020-01-01".
            end_date: Query period ending day, format "2020-01-01".
            sensors: The satellite sensors to search for, one or multiple of
                ["pleiades", "spot", "sentinel1", "sentinel2", "sentinel3", "sentinel5p"]
            limit: The maximum number of search results to return (1-max.500).
            max_cloudcover: Maximum cloudcover % - e.g. 100 will return all scenes,
                8.4 will return all scenes with 8.4 or less cloudcover.
                Ignored for sensors that have no cloudcover (e.g. sentinel1).
            sortby: The property to sort by, "cloudCoverage", "acquisitionDate",
                "acquisitionIdentifier", "incidenceAngle", "snowCover".
            ascending: Ascending sort order by default, descending if False.

        Returns:
            The constructed parameters dictionary.
        """
        datetime = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
        block_filters: List[str] = []
        for sensor in sensors:
            if sensor not in list(supported_sensors.keys()):
                raise ValueError(
                    f"Currently only these sensors are supported: "
                    f"{list(supported_sensors.keys())}"
                )
            block_filters.extend(supported_sensors[sensor]["blocks"])

        aoi_fc = any_vector_to_fc(
            vector=geometry,
        )
        aoi_geometry = fc_to_query_geometry(
            fc=aoi_fc,
            geometry_operation="intersects",
            squash_multiple_features="union",
        )

        sort_order = "asc" if ascending else "desc"
        query_filters = {"dataBlock": {"in": block_filters}}
        if sensors != ["sentinel1"]:
            query_filters["cloudCoverage"] = {"lte": max_cloudcover}  # type: ignore

        search_parameters = {
            "datetime": datetime,
            "intersects": aoi_geometry,
            "limit": limit,
            "query": query_filters,
            "sortby": [{"field": f"properties.{sortby}", "direction": sort_order}],
        }
        return search_parameters

    def search(
        self, search_parameters: Dict, as_dataframe: bool = True
    ) -> Union[GeoDataFrame, Dict]:
        """
        Searches the catalog for the the search parameters and returns the metadata of
        the matching scenes.

        Args:
            search_parameters: The catalog search parameters, see example.
            as_dataframe: return type, GeoDataFrame if True (default), FeatureCollection if False.

        Returns:
            The search results as a GeoDataFrame, optionally as json dict.

        Example:
            ```python
                search_parameters={
                    "datetime": "2019-01-01T00:00:00Z/2019-01-15T23:59:59Z",
                    "intersects": {
                        "type": "Polygon",
                        "coordinates": [[[13.32113746,52.73971768],[13.15981158,52.2092959],
                        [13.62204483,52.15632025],[13.78859517,52.68655119],[13.32113746,
                        52.73971768]]]},
                    "limit": 10,
                    "sortby": [{"field" : "properties.acquisitionDate", "direction" : "asc"}]
                    }
            ```
        """
        logger.info(f"Searching catalog with search_parameters: {search_parameters}")
        url = f"{self.auth._endpoint()}/catalog/stac/search"
        response_json = self.auth._request("POST", url, search_parameters)
        logger.info(f"{len(response_json['features'])} results returned.")
        dst_crs = "EPSG:4326"
        df = GeoDataFrame.from_features(response_json, crs=dst_crs)
        if df.empty:
            if as_dataframe:
                return df
            else:
                return df.__geo_interface__

        # Filter to actual geometries intersecting the aoi (Sobloo search uses a rectangular
        # bounds geometry, can contain scenes that touch the aoi bbox, but not the aoi.
        # So number returned images not consistent with set limit.
        # TODO: Resolve on backend
        geometry = search_parameters["intersects"]
        poly = shape(geometry)
        df = df[df.intersects(poly)]
        df = df.reset_index(drop=True)

        # Make scene_id more easily accessible
        def _get_scene_id(row):
            if row["providerName"] == "oneatlas":
                row["scene_id"] = row["providerProperties"]["parentIdentifier"]
            elif row["providerName"] in ["sobloo-radar", "sobloo-image"]:
                row["scene_id"] = row["providerProperties"]["identification"][
                    "externalId"
                ]
            return row

        # Search result dataframe can contain scenes of multiple sensors, need to apply row by row.
        df = df.apply(_get_scene_id, axis=1)
        df.crs = dst_crs  # apply resets the crs

        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def download_quicklooks(
        self,
        image_ids: List[str],
        sensor: str,
        output_directory: Union[str, Path] = None,
    ) -> List[str]:
        """
        Gets the quicklooks of scenes from a single sensor. After download, can
        be plotted via catalog.plot_quicklooks() or catalog.map_quicklooks().

        Args:
            image_ids: List of provider image_ids e.g. ["6dffb8be-c2ab-46e3-9c1c-6958a54e4527"].
                Access the search results id column via `list(search_results.id)`.
            sensor: The satellite sensor of the image_ids, one of "pleiades", "spot",
                "sentinel1", "sentinel2", "sentinel3", "sentinel5p".
            output_directory: The file output directory, defaults to the current working
                directory.

        Returns:
            List of quicklook image output file paths.
        """
        if sensor not in list(supported_sensors.keys()):
            raise ValueError(
                f"Currently only these sensors are supported: "
                f"{list(supported_sensors.keys())}"
            )
        provider = supported_sensors[sensor]["provider"]
        logger.info(
            f"Getting quicklooks from provider {provider} for image_ids: "
            f"{image_ids}"
        )

        if output_directory is None:
            output_directory = Path.cwd() / f"project_{self.auth.project_id}/catalog"
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

        if isinstance(image_ids, str):
            image_ids = [image_ids]

        out_paths: List[str] = []
        for image_id in tqdm(image_ids):
            try:
                url = f"{self.auth._endpoint()}/catalog/{provider}/image/{image_id}/quicklook"

                response = self.auth._request(
                    request_type="GET", url=url, return_text=False
                )
                out_path = output_directory / f"quicklook_{image_id}.jpg"
                out_paths.append(str(out_path))
                with open(out_path, "wb") as dst:
                    for chunk in response:
                        dst.write(chunk)
            except ValueError:
                logger.warning(
                    f"Image with id {image_id} does not have quicklook available. Skipping ..."
                )

        self.quicklooks = out_paths  # pylint: disable=attribute-defined-outside-init
        return out_paths
