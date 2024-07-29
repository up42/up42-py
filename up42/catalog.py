"""
Catalog search functionality
"""

import pathlib
import warnings
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

import geojson  # type: ignore
import geopandas  # type: ignore
import tqdm
from shapely import geometry as geom  # type: ignore

from up42 import auth as up42_auth
from up42 import base, host, order, utils

logger = utils.get_logger(__name__)


class ResolutionValue(TypedDict):
    minimum: float
    maximum: Optional[float]


class Host(TypedDict):
    # pylint: disable=invalid-name
    name: str
    title: str
    description: str
    createdAt: Optional[str]
    updatedAt: Optional[str]
    isIntegrated: bool
    isCommercial: bool


class Producer(TypedDict):
    # pylint: disable=invalid-name
    name: str
    title: str
    description: str
    createdAt: Optional[str]
    updatedAt: Optional[str]
    isIntegrated: bool


CollectionType = Literal["ARCHIVE", "TASKING"]


class Collection(TypedDict):
    # pylint: disable=invalid-name
    name: str
    title: str
    description: str
    type: CollectionType
    restricted: bool
    createdAt: Optional[str]
    updatedAt: Optional[str]
    host: Host
    # Deprecated
    hostName: str
    producer: Producer
    # Deprecated
    producerName: str
    isIntegrated: bool
    # Deprecated
    isOptical: bool
    resolutionClass: Literal["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]
    productType: Literal["OPTICAL", "SAR", "ELEVATION"]
    resolutionValue: ResolutionValue


class ProductConfiguration(TypedDict):
    # pylint: disable=invalid-name
    host: Host
    hostName: str
    title: str
    description: str
    id: str
    configuration: dict
    createdAt: Optional[str]
    updatedAt: Optional[str]
    isIntegrated: bool


class DataProduct(TypedDict):
    # pylint: disable=invalid-name
    id: str
    # Deprecated
    productConfiguration: ProductConfiguration
    # Deprecated
    productConfigurationId: str
    collection: Collection
    # Deprecated
    collectionName: str
    createdAt: Optional[str]
    updatedAt: Optional[str]
    isIntegrated: bool


class CollectionOverview(TypedDict):
    collection: str
    host: str
    data_products: dict[str, str]


PRODUCT_GLOSSARY_PARAMS = {"is_integrated": "true", "paginated": "false"}


class ProductGlossary:
    session = base.Session()

    @classmethod
    def get_collections(cls, collection_type: Optional[CollectionType]) -> list[Collection]:
        """
        Get the available data collections.
        """
        url = host.endpoint("/collections")
        integrated_collections = cls.session.get(url, params=PRODUCT_GLOSSARY_PARAMS).json()["data"]
        return [collection for collection in integrated_collections if collection["type"] == collection_type]

    @classmethod
    def get_data_products(
        cls, collection_type: Optional[CollectionType], grouped: bool
    ) -> Union[List[DataProduct], dict[str, CollectionOverview]]:
        """
        Get the available data product information for each collection. A data
        product is the available data configurations for each collection,
        e.g. Pleiades Display product.

        Args:
            collection_type: The type of the target collections
            grouped: A dictionary containing only the collection title,
                name, host and available data product configurations,
                default True.
        """
        url = host.endpoint("/data-products")
        integrated_products: list[DataProduct] = cls.session.get(url, params=PRODUCT_GLOSSARY_PARAMS).json()["data"]

        products = []
        for product in integrated_products:
            if product["collection"]["type"] != collection_type:
                continue
            products.append(product)

        if grouped:
            overview: dict[str, CollectionOverview] = {}
            for product in products:
                collection_title = product["collection"]["title"]
                collection_name = product["collection"]["name"]
                host_name = product["collection"]["host"]["name"]
                data_product = {product["productConfiguration"]["title"]: product["id"]}
                collection_info: CollectionOverview = {
                    "collection": collection_name,
                    "host": host_name,
                    "data_products": {},
                }
                overview.setdefault(collection_title, collection_info)["data_products"].update(data_product)

            return overview
        return products


class CatalogBase:
    """
    The base for Catalog and Tasking class, shared functionality.
    """

    session = base.Session()

    def __init__(self, auth: up42_auth.Auth, workspace_id: str):
        self.auth = auth
        self.workspace_id = workspace_id
        # FIXME: cannot be optional
        self.type: Optional[CollectionType] = None

    def get_collections(self) -> list[Collection]:
        return ProductGlossary.get_collections(self.type)

    @utils.deprecation("ProductGlossary::get_collections", "2.0.0")
    def get_data_products(self, basic: bool = True) -> Union[List[DataProduct], dict[str, CollectionOverview]]:
        return ProductGlossary.get_data_products(self.type, basic)

    def get_data_product_schema(self, data_product_id: str) -> dict:
        """
        Gets the parameters schema of a data product to help
        with the construction of the catalog/tasking order
        parameters.

        Args:
            data_product_id: The id of a catalog/tasking data product.
        """
        url = host.endpoint(f"/orders/schema/{data_product_id}")
        return self.auth.request("GET", url)

    def place_order(
        self,
        order_parameters: Optional[Dict],
        track_status: bool = False,
        report_time: int = 120,
        **kwargs,
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

        Warning "Deprecated order parameters"
            The use of the 'scene' and 'geometry' parameters for
            the data ordering is deprecated. Please use the new
            order_parameters parameter as described above.

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
        if "scene" in kwargs or "geometry" in kwargs:
            # Deprecated, to be removed, use order_parameters.
            message = (
                "The use of the 'scene' and 'geometry' parameters "
                "for the data ordering is deprecated. "
                "Please use the new 'order_parameters' parameter."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
        elif order_parameters is None:
            raise ValueError("Please provide the 'order_parameters' parameter!")
        placed_order = order.Order.place(self.auth, order_parameters, self.workspace_id)  # type: ignore
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

    def __init__(self, auth: up42_auth.Auth, workspace_id: str):
        super().__init__(auth, workspace_id)
        self.type = "ARCHIVE"

    def estimate_order(self, order_parameters: Optional[Dict], **kwargs) -> int:
        """
        Estimate the cost of an order.

        Args:
            order_parameters: A dictionary like
            {dataProduct: ..., "params": {"id": ..., "aoi": ...}}

        Returns:
            int: An estimated cost for the order in UP42 credits.

        Warning "Deprecated order parameters"
            The use of the 'scene' and 'geometry' parameters for
            the data estimation is deprecated. Please use the new
            order_parameters parameter as described above.
        """
        if "scene" in kwargs or "geometry" in kwargs:
            # Deprecated, to be removed, use order_parameters.
            message = (
                "The use of the 'scene' and 'geometry' parameters "
                "for the data estimation is deprecated. "
                "Please use the new 'order_parameters' parameter."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
        elif order_parameters is None:
            raise ValueError("Please provide the 'order_parameters' parameter!")
        return order.Order.estimate(self.auth, order_parameters)  # type: ignore

    @staticmethod
    def construct_search_parameters(
        geometry: Union[
            geojson.FeatureCollection,
            geojson.Feature,
            dict,
            list,
            geopandas.GeoDataFrame,
            geom.Polygon,
        ],
        collections: List[str],
        start_date: str = "2020-01-01",
        end_date: str = "2020-01-30",
        usage_type: Optional[List[str]] = None,
        limit: int = 10,
        max_cloudcover: Optional[int] = None,
        sortby: Optional[str] = None,
        ascending: Optional[bool] = None,
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
            sortby: (deprecated)
            ascending: (deprecated)
        Returns:
            The constructed parameters dictionary.
        """

        if sortby is not None or ascending is not None:
            logger.info("sortby is deprecated, currently only sorting output by creation date.")
        start = utils.format_time(start_date)
        end = utils.format_time(end_date, set_end_of_day=True)
        time_period = f"{start}/{end}"

        aoi_fc = utils.any_vector_to_fc(
            vector=geometry,
        )
        aoi_geometry = utils.fc_to_query_geometry(fc=aoi_fc, geometry_operation="intersects")

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

        return {
            "datetime": time_period,
            "intersects": aoi_geometry,
            "limit": limit,
            "collections": collections,
            "query": query_filters,
        }

    def _get_host(self, collections: list[str]) -> str:
        # FIXME: switch to using collections info instead of data products
        data_products = cast(dict[str, CollectionOverview], self.get_data_products(basic=True))
        hosts = {product["host"] for product in data_products.values() if product["collection"] in collections}
        if not hosts:
            raise ValueError(f"Selected collections {collections} are not valid. See catalog.get_collections.")
        if len(hosts) > 1:
            raise ValueError("Only collections with the same host can be searched at the same time.")
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
        aoi: Union[
            dict,
            geojson.Feature,
            geojson.FeatureCollection,
            list,
            geopandas.GeoDataFrame,
            geom.Polygon,
        ] = None,
        tags: Optional[List[str]] = None,
    ):
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
        order_parameters = {
            "dataProduct": data_product_id,
            "params": {"id": image_id},
        }
        if tags is not None:
            order_parameters["tags"] = tags
        schema = self.get_data_product_schema(data_product_id)
        order_parameters = utils.autocomplete_order_parameters(order_parameters, schema)

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
