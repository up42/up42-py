"""
Catalog search functionality
"""

from pathlib import Path
from typing import Union, List, Tuple, Dict, Any

from pandas import Series
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection
from tqdm import tqdm

from up42.auth import Auth
from up42.viztools import VizTools
from up42.order import Order
from up42.utils import (
    get_logger,
    any_vector_to_fc,
    fc_to_query_geometry,
    format_time_period,
)

logger = get_logger(__name__)


# pylint: disable=duplicate-code
class Catalog(VizTools):
    """
    The Catalog class enables access to the UP42 catalog search. You can search
    for satellite image scenes (for different sensors and criteria like cloud cover),
    plot the scene coverage and download and plot the scene quicklooks.

    Use the catalog:
    ```python
    catalog = up42.initialize_catalog()
    ```
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.quicklooks = None

    def __repr__(self):
        return f"Catalog(auth={self.auth})"

    def get_collections(self) -> Union[Dict, List]:
        """
        Get the available data collections.
        """
        url = f"{self.auth._endpoint()}/collections"
        json_response = self.auth._request("GET", url)
        return json_response["data"]

    # pylint: disable=dangerous-default-value
    @staticmethod
    def construct_parameters(
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ],
        collections: List[str],
        start_date: str = "2020-01-01",
        end_date: str = "2020-01-30",
        usage_type: List[str] = ["DATA", "ANALYTICS"],
        limit: int = 10,
        max_cloudcover: float = 100,
        sortby: str = "acquisitionDate",
        ascending: bool = True,
    ) -> dict:
        """
        Follows STAC principles and property names.

        Args:
            geometry: The search geometry, one of dict, Feature, FeatureCollection,
                list, GeoDataFrame, Polygon.
            collections: The satellite sensor collections to search for, e.g. ["phr"] or ["phr", "spot"].
                Also see catalog.get_collections().
            start_date: Query period starting day, format "2020-01-01".
            end_date: Query period ending day, format "2020-01-01".
            usage_type: Filter for imagery that can just be purchased & downloaded or also
                processes. ["DATA"] (can only be download), ["ANALYTICS"] (can be downloaded
                or used directly with a processing algorithm), ["DATA", "ANALYTICS"]
                (can be any combination). The filter is inclusive, using ["DATA"] can
                also result in results with ["DATA", "ANALYTICS"].
            limit: The maximum number of search results to return (1-max.500).
            max_cloudcover: Maximum cloudcover % - e.g. 100 will return all scenes,
                8.4 will return all scenes with 8.4 or less cloudcover.
                Ignored for collections that have no cloudcover (e.g. sentinel1).
            sortby: The property to sort by, "cloudCoverage", "acquisitionDate",
                "acquisitionIdentifier", "incidenceAngle", "snowCover".
            ascending: Ascending sort order by default, descending if False.

        Returns:
            The constructed parameters dictionary.
        """
        time_period = format_time_period(start_date=start_date, end_date=end_date)
        aoi_fc = any_vector_to_fc(
            vector=geometry,
        )
        aoi_geometry = fc_to_query_geometry(fc=aoi_fc, geometry_operation="intersects")
        sort_order = "asc" if ascending else "desc"

        query_filters: Dict[Any, Any] = {}
        if not "Sentinel-1" in collections:
            query_filters["cloudCoverage"] = {"lte": max_cloudcover}  # type: ignore

        if usage_type == ["DATA"]:
            query_filters["up42:usageType"] = {"in": ["DATA"]}
        elif usage_type == ["ANALYTICS"]:
            query_filters["up42:usageType"] = {"in": ["ANALYTICS"]}
        elif usage_type == ["DATA", "ANALYTICS"]:
            query_filters["up42:usageType"] = {"in": ["DATA", "ANALYTICS"]}
        else:
            raise ValueError("Select correct `usage_type`")

        search_parameters = {
            "datetime": time_period,
            "intersects": aoi_geometry,
            "limit": limit,
            "collections": collections,
            "query": query_filters,
            "sortby": [{"field": f"properties.{sortby}", "direction": sort_order}],
        }

        return search_parameters

    def search(
        self, search_parameters: dict, as_dataframe: bool = True
    ) -> Union[GeoDataFrame, dict]:
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
                    "collections": ["phr"],
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

        # The API request would fail with a limit above 500, thus 500 is forced in the initial
        # request but additional results are handled below via pagination.
        max_limit = search_parameters["limit"]
        if max_limit > 500:
            search_parameters = dict(search_parameters)
            search_parameters["limit"] = 500

        # UP42 API can query multiple collections of the same host at once.
        collections = self.get_collections()
        hosts = [
            c["hostName"]
            for c in collections
            if c["name"] in search_parameters["collections"]
        ]
        if not hosts:
            raise ValueError(
                f"Selected collections {search_parameters['collections']} are not valid. See "
                f"catalog.get_collections."
            )
        if len(set(hosts)) > 1:
            raise ValueError(
                "Only collections with the same host can be searched at the same time. Please adjust the "
                "collections in the search_parameters!"
            )
        host = hosts[0]

        url = f"{self.auth._endpoint()}/catalog/hosts/{host}/stac/search"
        response_json: dict = self.auth._request("POST", url, search_parameters)
        features = response_json["features"]

        # Search results with more than 500 items are given as 50-per-page additional pages.
        while len(features) < max_limit:
            pagination_exhausted = len(response_json["links"]) == 1
            if pagination_exhausted:
                break
            next_page_url = response_json["links"][1]["href"]
            response_json = self.auth._request("POST", next_page_url, search_parameters)
            features += response_json["features"]

        features = features[:max_limit]
        df = GeoDataFrame.from_features(
            FeatureCollection(features=features), crs="EPSG:4326"
        )

        logger.info(f"{df.shape[0]} results returned.")
        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def download_quicklooks(
        self,
        image_ids: List[str],
        sensor: str,
        output_directory: Union[str, Path, None] = None,
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
        supported_sensors = {
            "pleiades": "oneatlas",
            "spot": "oneatlas",
            "sentinel1": "sobloo-image",
            "sentinel2": "sobloo-image",
            "sentinel3": "sobloo-image",
            "sentinel5p": "sobloo-image",
        }

        if sensor not in list(supported_sensors.keys()):
            raise ValueError(
                f"Currently only these sensors are supported: "
                f"{list(supported_sensors.keys())}"
            )
        provider = supported_sensors[sensor]
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

    @staticmethod
    def _order_payload(
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ],
        scene: Series,
    ) -> Tuple[str, dict]:
        """
        Helper that constructs necessary parameters for `Order.place` and `Order.estimate`.

        Args:
            geometry: The intended output AOI of the order, one of dict, Feature, FeatureCollection, list,
                GeoDataFrame, Polygon.
            scene: A geopandas series with a  single item/row of the result of `Catalog.search`. For instance,
                search_results.loc[0] for the first scene of a catalog search result.

        Returns:
            str, dict: A tuple including a provider name and order parameters.
        """
        if not isinstance(scene, Series):
            raise ValueError(
                "`scene` parameter must be a GeoSeries, or a single item/row of a GeoDataFrame. "
                "For instance, search_results.loc[0] returns a GeoSeries."
            )
        aoi_fc = any_vector_to_fc(
            vector=geometry,
        )
        aoi_geometry = fc_to_query_geometry(fc=aoi_fc, geometry_operation="intersects")
        data_provider_name = scene.providerName
        order_params = {"id": scene.id, "aoi": aoi_geometry}
        return data_provider_name, order_params

    def estimate_order(
        self,
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ],
        scene: Series,
    ) -> int:
        """
        Estimate the cost of an order from an item/row in a result of `Catalog.search`.

        Args:
            geometry: The intended output AOI of the order, one of dict, Feature, FeatureCollection, list,
                GeoDataFrame, Polygon.
            scene: A geopandas series with a  single item/row of the result of `Catalog.search`. For instance,
                search_results.loc[0] for the first scene of a catalog search result.

        Returns:
            int: An estimated cost for the order in UP42 credits.
        """
        data_provider_name, order_params = self._order_payload(geometry, scene)
        return Order.estimate(self.auth, data_provider_name, order_params)

    def place_order(
        self,
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ],
        scene: Series,
        track_status: bool = False,
        report_time: int = 120,
    ) -> "Order":
        """
        Place an order from an item/row in a result of `Catalog.search`.

        Args:
            geometry: The intended output AOI of the order, one of dict, Feature, FeatureCollection, list,
                GeoDataFrame, Polygon.
            scene: A geopandas series with a  single item/row of the result of `Catalog.search`. For instance,
                search_results.loc[0] for the first scene of a catalog search result.
            track_status (bool): If set to True, will only return the Order once it is `FULFILLED` or `FAILED`.
            report_time (int): The interval (in seconds) to query the order status if `track_status` is True.

         Warning:
            When placing orders of items that are in archive or cold storage,
            the order fulfillment can happen up to **24h after order placement**.
            In such cases, please make sure to set an appropriate `report_time`.
            You can also use `Order.track_status` on the returned object to track the status later.

        Returns:
            Order: The placed order.
        """
        data_provider_name, order_params = self._order_payload(geometry, scene)
        order = Order.place(self.auth, data_provider_name, order_params)
        if track_status:
            order.track_status(report_time)
        return order
