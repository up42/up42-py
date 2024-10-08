"""
Catalog search functionality
"""

import pathlib
from typing import Any, Dict, List, Literal, Optional, Union

import geojson  # type: ignore
import geopandas  # type: ignore
import tqdm
from shapely import geometry as geom  # type: ignore

from up42 import base, glossary, host, order, utils

logger = utils.get_logger(__name__)

Geometry = Union[
    dict,
    geojson.Feature,
    geojson.FeatureCollection,
    list,
    geopandas.GeoDataFrame,
    geom.Polygon,
]


class InvalidUsageType(ValueError):
    pass


class InvalidCollections(ValueError):
    pass


class MultipleHosts(ValueError):
    pass


class CatalogBase:
    """
    The base for Catalog and Tasking class, shared functionality.
    """

    session = base.Session()
    workspace_id = base.WorkspaceId()

    def __init__(self, collection_type: glossary.CollectionType):
        self.type = collection_type

    def get_data_product_schema(self, data_product_id: str) -> dict:
        """
        Gets the parameters schema of a data product to help
        with the construction of the catalog/tasking order
        parameters.

        Args:
            data_product_id: The id of a catalog/tasking data product.
        """
        url = host.endpoint(f"/orders/schema/{data_product_id}")
        return self.session.get(url).json()

    def estimate_order(self, order_parameters: order.OrderParams) -> int:
        """
        Estimate the cost of an order.

        Args:
            order_parameters: A dictionary like
            {dataProduct: ..., "params": {"id": ..., "aoi": ...}}

        Returns:
            int: An estimated cost for the order in UP42 credits.
        """

        return order.Order.estimate(order_parameters)

    def place_order(
        self,
        order_parameters: order.OrderParams,
        track_status: bool = False,
        report_time: float = 120,
    ) -> order.Order:
        """
        Place an order.

        Args:
            order_parameters: A dictionary like
                {dataProduct: ..., "params": {"id": ..., "aoi": ...}}
            track_status (bool): If set to True, will only return
                the Order once it is `FULFILLED` or `FAILED`.
            report_time (int): The interval (in seconds) to query
                the order status if `track_status` is True.

         Warning:
            When placing orders of items that are in
            archive or cold storage,
            the order fulfillment can happen up to
            **24h after order placement**.
            In such cases, please make sure to set
            an appropriate `report_time`.
            You can also use `Order.track_status` on the
            returned object to track the status later.

        Returns:
            Order class object of the placed order.
        """
        placed_order = order.Order.place(order_parameters, self.workspace_id)
        if track_status:
            placed_order.track_status(report_time)
        return placed_order


class Catalog(CatalogBase):
    """
    The Catalog class enables access to the UP42 catalog
    functionality (data archive search & ordering).

    Use catalog:
    ```python
    catalog = up42.initialize_catalog()
    ```

    This class also inherits functions from the
    [CatalogBase](catalogbase-reference.md) class.
    """

    def __init__(self):
        super().__init__(glossary.CollectionType.ARCHIVE)

    @staticmethod
    def construct_search_parameters(
        geometry: Geometry,
        collections: List[str],
        start_date: str = "2020-01-01",
        end_date: str = "2020-01-30",
        usage_type: Optional[List[Literal["DATA", "ANALYTICS"]]] = None,
        limit: int = 10,
        max_cloudcover: Optional[int] = None,
    ) -> dict:
        """
        Helps constructing the parameters dictionary required for the search.

        Args:
            geometry: The search geometry, default a Polygon.
                One of FeatureCollection, Feature, dict (geojson geometry),
                list (bounds coordinates), GeoDataFrame,
                shapely.Polygon, shapely.Point.
                All assume EPSG 4326!
            collections: The satellite sensor collections to search for,
                e.g. ["phr"] or ["phr", "spot"].
                Also see catalog.get_collections().
            start_date: Query period starting day, format "2020-01-01".
            end_date: Query period ending day, format "2020-01-01".
            usage_type: Optional. Filter for imagery that can
                be purchased & downloaded or also processed.
                ["DATA"] (can only be downloaded),
                ["ANALYTICS"] (can be downloaded
                or used directly with a processing algorithm),
                ["DATA", "ANALYTICS"] (can be any combination).
                The filter is inclusive, using ["DATA"] can
                also result in results with ["DATA", "ANALYTICS"].
            limit: The maximum number of search results to return (1-max.500).
            max_cloudcover: Optional. Maximum cloud coverage percent.
                e.g. 100 will return all scenes,
                8.4 will return all scenes with 8.4 or less cloud coverage.
        Returns:
            The constructed parameters dictionary.
        """

        start = utils.format_time(start_date)
        end = utils.format_time(end_date, set_end_of_day=True)
        time_period = f"{start}/{end}"

        aoi_fc = utils.any_vector_to_fc(
            vector=geometry,
        )
        aoi_geometry = utils.fc_to_query_geometry(fc=aoi_fc, geometry_operation="intersects")

        query_filters: Dict[Any, Any] = {}
        if max_cloudcover is not None:
            query_filters["cloudCoverage"] = {"lte": max_cloudcover}

        if usage_type is not None:
            if set(usage_type) <= {"DATA", "ANALYTICS"}:
                query_filters["up42:usageType"] = {"in": usage_type}
            else:
                raise InvalidUsageType("usage_type is invalid")

        return {
            "datetime": time_period,
            "intersects": aoi_geometry,
            "limit": limit,
            "collections": collections,
            "query": query_filters,
        }

    def _get_host(self, collection_names: list[str]) -> str:
        collections = glossary.ProductGlossary.get_collections(collection_type=self.type)
        hosts = {
            provider.name
            for collection in collections
            if collection.name in collection_names
            for provider in collection.providers
            if "HOST" in provider.roles
        }

        if not hosts:
            raise InvalidCollections(
                f"Selected collections {collection_names} are not valid. See ProductGlossary.get_collections."
            )
        if len(hosts) > 1:
            raise MultipleHosts("Only collections with the same host can be searched at the same time.")
        return hosts.pop()

    def search(self, search_parameters: dict, as_dataframe: bool = True) -> Union[geopandas.GeoDataFrame, dict]:
        """
        Searches the catalog  and returns the metadata of the matching scenes.

        Args:
            search_parameters: The catalog search parameters, see example.
            as_dataframe: return type, geopandas.GeoDataFrame if True (default),
                FeatureCollection if False.

        Returns:
            The search results as a geopandas.GeoDataFrame,
            optionally as JSON dict.

        Example:
            ```python
                search_parameters={
                    "datetime": "2019-01-01T00:00:00Z/2019-01-15T23:59:59Z",
                    "collections": ["phr"],
                    "intersects": {
                        "type": "Polygon",
                        "coordinates": [[[13.32113746,52.73971768],
                        [13.15981158,52.2092959],[13.62204483,52.15632025],
                        [13.78859517,52.68655119],[13.32113746,
                        52.73971768]]]},
                    "limit": 10,
                    "sortby": [{"field" : "properties.acquisitionDate",
                        "direction" : "asc"}]
                    }
            ```
        """
        logger.info("Searching catalog with search_parameters: %s", search_parameters)

        if "limit" in search_parameters:
            search_parameters["limit"] = min(search_parameters["limit"], 500)

        product_host = self._get_host(search_parameters["collections"])
        url = host.endpoint(f"/catalog/hosts/{product_host}/stac/search")
        features = []

        while url:
            page: dict = self.session.post(url, json=search_parameters).json()
            features += page["features"]
            url = next((link["href"] for link in page["links"] if link["rel"] == "next"), None)

        if not features:
            df = geopandas.GeoDataFrame(columns=["geometry"], geometry="geometry")
        else:
            df = geopandas.GeoDataFrame.from_features(geojson.FeatureCollection(features=features), crs="EPSG:4326")

        logger.info("%s results returned.", df.shape[0])
        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def construct_order_parameters(
        self,
        data_product_id: str,
        image_id: str,
        aoi: Optional[Geometry] = None,
        tags: Optional[List[str]] = None,
    ) -> order.OrderParams:
        """
        Helps constructing the parameters dictionary required
        for the catalog order. Some collections have
        additional parameters that are added to the output
        dictionary with value None. The potential values to
        select from are given in the logs, for more detail on
        the parameter use `catalog.get_data_product_schema()`.

        Args:
            data_product_id: Id of the desired UP42 data product,
                see `catalog.get_data_products`
            image_id: The id of the desired image
                (from search results)
            aoi: The geometry of the order, one of dict, Feature,
                FeatureCollection, list, geopandas.GeoDataFrame, Polygon.
                Optional for "full-image products".
            tags: A list of tags that categorize the order.
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
        schema = self.get_data_product_schema(data_product_id)
        params: dict[str, Any] = {param: None for param in schema["required"]}
        params["id"] = image_id
        order_parameters: order.OrderParams = {"dataProduct": data_product_id, "params": params}
        if tags is not None:
            order_parameters["tags"] = tags

        # Some catalog orders, e.g. Capella don't require AOI (full image order)
        # Handled on API level, don't manipulate in SDK,
        # providers might accept geometries in the future.
        if aoi is not None:
            aoi = utils.any_vector_to_fc(vector=aoi)
            aoi = utils.fc_to_query_geometry(fc=aoi, geometry_operation="intersects")
            order_parameters["params"]["aoi"] = aoi  # type: ignore

        return order_parameters

    def download_quicklooks(
        self,
        image_ids: List[str],
        collection: str,
        output_directory: Union[str, pathlib.Path, None] = None,
    ) -> List[str]:
        """
        Gets the quicklooks of scenes from a single sensor.

        Args:
            image_ids: List of provider image_ids
                e.g. ["6dffb8be-c2ab-46e3-9c1c-6958a54e4527"].
                Access the search results id column via
                `list(search_results.id)`.
            collection: The data collection corresponding to the image ids.
            output_directory: The file output directory,
                defaults to the current working directory.

        Returns:
            List of quicklook image output file paths.
        """
        product_host = self._get_host([collection])
        logger.info("Downloading quicklooks from provider %s.", product_host)

        if output_directory is None:
            output_directory = pathlib.Path.cwd() / "catalog"
        else:
            output_directory = pathlib.Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Download directory: %s", output_directory)

        out_paths: List[str] = []
        for image_id in tqdm.tqdm(image_ids):
            try:
                url = host.endpoint(f"/catalog/{product_host}/image/{image_id}/quicklook")
                response = self.session.get(url)
                # TODO: should detect extensions based on response content type
                # TODO: to be simplified using utils.download_file
                out_path = str(output_directory / f"quicklook_{image_id}.jpg")
                with open(out_path, "wb") as dst:
                    for chunk in response:
                        dst.write(chunk)
                out_paths.append(out_path)
            except IOError:
                logger.warning(
                    "Image with id %s does not have quicklook available. Skipping ...",
                    image_id,
                )
        return out_paths
