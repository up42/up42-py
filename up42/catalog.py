"""
Catalog search functionality
"""

from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import warnings

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
    deprecation,
    autocomplete_order_parameters,
    format_time,
)

logger = get_logger(__name__)


class CatalogBase:
    """
    The base for Catalog and Tasking class, shared functionality.
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.type: Union[str, None] = None

    def get_data_products(self, basic: bool = True) -> Union[dict, List[dict]]:
        """
        Get the available data product information for each collection. A data product is the available
        data configurations for each collection, e.g. Pleiades Display product.

        Args:
            basic: A dictionary containing only the collection title, name, host and available
                data product configurations, default True.
        """
        url = f"{self.auth._endpoint()}/data-products"
        json_response = self.auth._request("GET", url)
        unfiltered_products: list = json_response["data"]

        products = []
        for product in unfiltered_products:
            if product["collection"]["type"] != self.type:
                continue
            try:
                if not product["collection"]["isIntegrated"]:
                    continue
            except KeyError:  # isIntegrated potentially removed from future public API
                pass
            try:
                if not product["productConfiguration"]["isIntegrated"]:
                    continue
            except KeyError:
                pass
            products.append(product)

        if not basic:
            return products
        else:
            collection_overview = {}
            for product in products:
                collection_title = product["collection"]["title"]
                collection_name = product["collectionName"]
                host = product["collection"]["host"]["name"]
                data_product = {product["productConfiguration"]["title"]: product["id"]}

                if collection_title not in collection_overview:
                    collection_overview[collection_title] = {
                        "collection": collection_name,
                        "host": host,
                        "data_products": data_product,
                    }
                else:
                    # Add additional products for same collection
                    collection_overview[collection_title]["data_products"][
                        product["productConfiguration"]["title"]
                    ] = product["id"]

            return collection_overview

    def get_data_product_schema(self, data_product_id: str) -> dict:
        """
        Gets the parameters schema of a data product to help with the construction of the catalog/tasking order
        parameters.

        Args:
            data_product_id: The id of a catalog/tasking data product.
        """
        url = f"{self.auth._endpoint()}/orders/schema/{data_product_id}"
        json_response = self.auth._request("GET", url)
        return json_response  # Does not contain APIv1 "data" key

    def get_collections(self) -> Union[Dict, List]:
        """
        Get the available data collections.
        """
        url = f"{self.auth._endpoint()}/collections"
        json_response = self.auth._request("GET", url)
        collections = [c for c in json_response["data"] if c["type"] == self.type]
        return collections

    def place_order(
        self,
        order_parameters: Union[dict, None],
        track_status: bool = False,
        report_time: int = 120,
        **kwargs,
    ) -> Order:
        """
        Place an order.

        Args:
            order_parameters: A dictionary like {dataProduct: ..., "params": {"id": ..., "aoi": ...}}
            track_status (bool): If set to True, will only return the Order once it is `FULFILLED` or `FAILED`.
            report_time (int): The interval (in seconds) to query the order status if `track_status` is True.

        Warning "Deprecated order parameters"
            The use of the 'scene' and 'geometry' parameters for the data ordering is deprecated. Please use the new
            order_parameters parameter as described above.

         Warning:
            When placing orders of items that are in archive or cold storage,
            the order fulfillment can happen up to **24h after order placement**.
            In such cases, please make sure to set an appropriate `report_time`.
            You can also use `Order.track_status` on the returned object to track the status later.

        Returns:
            Order class object of the placed order.
        """
        if "scene" in kwargs or "geometry" in kwargs:
            # Deprecated, to be removed, use order_parameters.
            message = (
                "The use of the 'scene' and 'geometry' parameters for the data ordering is deprecated. "
                "Please use the new 'order_parameters' parameter."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
        elif order_parameters is None:
            raise ValueError("Please provide the 'order_parameters' parameter!")

        order = Order.place(self.auth, order_parameters)  # type: ignore
        if track_status:
            order.track_status(report_time)
        return order


class Catalog(CatalogBase, VizTools):
    """
    The Catalog class enables access to the UP42 catalog functionality (data archive search & ordering).

    Use catalog:
    ```python
    catalog = up42.initialize_catalog()
    ```
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.quicklooks = None
        self.type = "ARCHIVE"
        self.data_products: Union[None, dict] = None

    def __repr__(self):
        return f"Catalog(auth={self.auth})"

    def estimate_order(self, order_parameters: Union[dict, None], **kwargs) -> int:
        """
        Estimate the cost of an order.

        Args:
            order_parameters: A dictionary like {dataProduct: ..., "params": {"id": ..., "aoi": ...}}

        Returns:
            int: An estimated cost for the order in UP42 credits.

        Warning "Deprecated order parameters"
            The use of the 'scene' and 'geometry' parameters for the data estimation is deprecated. Please use the new
            order_parameters parameter as described above.
        """
        if "scene" in kwargs or "geometry" in kwargs:
            # Deprecated, to be removed, use order_parameters.
            message = (
                "The use of the 'scene' and 'geometry' parameters for the data estimation is deprecated. "
                "Please use the new 'order_parameters' parameter."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
        elif order_parameters is None:
            raise ValueError("Please provide the 'order_parameters' parameter!")
        return Order.estimate(self.auth, order_parameters)  # type: ignore

    @deprecation("construct_search_parameters", "0.25.0")
    def construct_parameters(self, **kwargs):  # pragma: no cover
        """Deprecated, see construct_search_parameters"""
        return self.construct_search_parameters(**kwargs)

    @staticmethod
    def construct_search_parameters(
        geometry: Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon],
        collections: List[str],
        start_date: str = "2020-01-01",
        end_date: str = "2020-01-30",
        usage_type: List[str] = None,
        limit: int = 10,
        max_cloudcover: Optional[int] = None,
        sortby: str = "acquisitionDate",
        ascending: bool = True,
    ) -> dict:
        """
        Helps constructing the parameters dictionary required for the search.

        Args:
            geometry: The search geometry, default a Polygon. One of FeatureCollection, Feature,
                dict (geojson geometry), list (bounds coordinates), GeoDataFrame, shapely.Polygon, shapely.Point.
                All assume EPSG 4326!
            collections: The satellite sensor collections to search for, e.g. ["phr"] or ["phr", "spot"].
                Also see catalog.get_collections().
            start_date: Query period starting day, format "2020-01-01".
            end_date: Query period ending day, format "2020-01-01".
            usage_type: Optional. Filter for imagery that can be purchased & downloaded or also
                processed. ["DATA"] (can only be downloaded), ["ANALYTICS"] (can be downloaded
                or used directly with a processing algorithm), ["DATA", "ANALYTICS"]
                (can be any combination). The filter is inclusive, using ["DATA"] can
                also result in results with ["DATA", "ANALYTICS"].
            limit: The maximum number of search results to return (1-max.500).
            max_cloudcover: Optional. Maximum cloudcover % - e.g. 100 will return all scenes,
                8.4 will return all scenes with 8.4 or less cloudcover.
            sortby: The property to sort by, "cloudCoverage", "acquisitionDate",
                "acquisitionIdentifier", "incidenceAngle", "snowCover".
            ascending: Ascending sort order by default, descending if False.

        Returns:
            The constructed parameters dictionary.
        """
        time_period = (
            f"{format_time(start_date)}/{format_time(end_date, set_end_of_day=True)}"
        )
        aoi_fc = any_vector_to_fc(
            vector=geometry,
        )
        aoi_geometry = fc_to_query_geometry(fc=aoi_fc, geometry_operation="intersects")
        sort_order = "asc" if ascending else "desc"

        query_filters: Dict[Any, Any] = {}
        if max_cloudcover is not None:
            query_filters["cloudCoverage"] = {"lte": max_cloudcover}  # type: ignore

        if usage_type is not None:
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
        try:
            max_limit = search_parameters["limit"]
        except KeyError:
            logger.info("No `limit` parameter in search_parameters, using default 500.")
            max_limit = 500

        if max_limit > 500:
            search_parameters["limit"] = 500

        # UP42 API can query multiple collections of the same host at once.
        if self.data_products is None:
            self.data_products = self.get_data_products(basic=True)  # type: ignore
        hosts = [
            v["host"]
            for v in self.data_products.values()  # type: ignore
            if v["collection"] in search_parameters["collections"]
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
        if not features:
            df = GeoDataFrame(columns=["geometry"], geometry="geometry")
        else:
            df = GeoDataFrame.from_features(
                FeatureCollection(features=features), crs="EPSG:4326"
            )

        logger.info(f"{df.shape[0]} results returned.")
        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def construct_order_parameters(
        self,
        data_product_id: str,
        image_id: str,
        aoi: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ] = None,
    ):
        """
        Helps constructing the parameters dictionary required for the catalog order. Some datasets have
        additional parameters that are added to the output dictionary with value None. The potential values to
        select from are given in the logs, for more detail on the parameter use `catalog.get_data_product_schema()`.

        Args:
            data_product_id: Id of the desired UP42 data product, see `catalog.get_data_products`
            image_id: The id of the desired image (from search results)
            aoi: The geometry of the order, one of dict, Feature, FeatureCollection,
                list, GeoDataFrame, Polygon. Optional for "full-image products".
        Returns:
            The order parameters dictionary.

        Example:
            ```python
            order_parameters = catalog.construct_order_parameters(
                data_product_id='647780db-5a06-4b61-b525-577a8b68bb54',
                image_id='6434e7af-2d41-4ded-a789-fb1b2447ac92',
                aoi={'type': 'Polygon',
                'coordinates': (((13.375966, 52.515068),
                  (13.375966, 52.516639),
                  (13.378314, 52.516639),
                  (13.378314, 52.515068),
                  (13.375966, 52.515068)),)})
            ```
        """
        order_parameters = {
            "dataProduct": data_product_id,
            "params": {"id": image_id},
        }
        logger.info(
            "See `catalog.get_data_product_schema(data_product_id)` for more detail on the parameter options."
        )
        schema = self.get_data_product_schema(data_product_id)
        order_parameters = autocomplete_order_parameters(order_parameters, schema)

        # Some catalog orders, e.g. Capella don't require aoi (full image order)
        # Handled on API level, don't manipulate in SDK, providers might accept geometries in the future.
        if aoi is not None:
            aoi = any_vector_to_fc(vector=aoi)
            aoi = fc_to_query_geometry(fc=aoi, geometry_operation="intersects")
            order_parameters["params"]["aoi"] = aoi  # type: ignore

        return order_parameters

    def download_quicklooks(
        self,
        image_ids: List[str],
        collection: str,
        output_directory: Union[str, Path, None] = None,
    ) -> List[str]:
        """
        Gets the quicklooks of scenes from a single sensor. After download, can
        be plotted via catalog.map_quicklooks() or catalog.plot_quicklooks().

        Args:
            image_ids: List of provider image_ids e.g. ["6dffb8be-c2ab-46e3-9c1c-6958a54e4527"].
                Access the search results id column via `list(search_results.id)`.
            collection: The data collection corresponding to the image ids.
            output_directory: The file output directory, defaults to the current working
                directory.

        Returns:
            List of quicklook image output file paths.
        """
        if self.data_products is None:
            self.data_products = self.get_data_products(basic=True)  # type: ignore
        host = [
            v["host"]
            for v in self.data_products.values()  # type: ignore
            if v["collection"] == collection
        ]
        if not host:
            raise ValueError(
                f"Selected collections {collection} is not valid. See catalog.get_collections."
            )
        host = host[0]
        logger.info(f"Downloading quicklooks from provider {host}.")

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
                url = (
                    f"{self.auth._endpoint()}/catalog/{host}/image/{image_id}/quicklook"
                )
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
