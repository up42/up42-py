from typing import List, Union, Optional, Dict, Any
import math
from datetime import datetime

from geopandas import GeoDataFrame
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection

from up42.auth import Auth
from up42.order import Order
from up42.asset import Asset
from up42.utils import get_logger, format_time, any_vector_to_fc, fc_to_query_geometry

logger = get_logger(__name__)


class Storage:
    """
    The Storage class enables access to the UP42 storage. You can list
    your assets and orders within an UP42 workspace.

    Use the storage:
    ```python
    storage = up42.initialize_storage()
    ```
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.workspace_id = auth.workspace_id

    def __repr__(self):
        env = ", env: dev" if self.auth.env == "dev" else ""
        return f"Storage(workspace_id: {self.workspace_id}{env})"

    def _query_paginated(
        self, url: str, limit: Optional[int] = None, size: int = 50
    ) -> List[dict]:
        """
        Helper to fetch list of items in paginated endpoint, e.g. assets, orders.

        Args:
            url (str): The base url for paginated endpoint.
            limit: Return n first elements sorted by date of creation, optional.
            size: Default number of results per pagination page. Tradeoff of number
                of results per page and API response time to query one page. Default 50.

        Returns:
            List[dict]: List of all paginated items.
        """
        url = url + f"&size={size}"

        first_page_response = self.auth._request(request_type="GET", url=url)
        if (
            "data" in first_page_response
        ):  # UP42 API v2 convention without data key, but still in e.g. get order
            # endpoint
            first_page_response = first_page_response["data"]
        num_pages = first_page_response["totalPages"]
        num_elements = first_page_response["totalElements"]
        results_list = first_page_response["content"]

        if limit is None:
            # Also covers single page (without limit)
            num_pages_to_query = num_pages
        elif limit <= size:
            return results_list[:limit]
        else:
            # Also covers single page (with limit)
            num_pages_to_query = math.ceil(min(limit, num_elements) / size)

        for page in range(1, num_pages_to_query):
            response_json = self.auth._request(
                request_type="GET", url=url + f"&page={page}"
            )
            if "data" in response_json:
                response_json = response_json["data"]
            results_list += response_json["content"]
        return results_list[:limit]

    def _search_stac(
        self,
        acquired_after: Optional[Union[str, datetime]] = None,
        acquired_before: Optional[Union[str, datetime]] = None,
        geometry: Optional[
            Union[
                dict,
                Feature,
                FeatureCollection,
                list,
                GeoDataFrame,
                Polygon,
            ]
        ] = None,
        custom_filter=None,
    ) -> list:
        """
        Search query for storage STAC collection items.

        Args:
            acquired_after: Filter for assets with image acquisition after the datetime or isoformat string e.g.
                "2022-01-01".
            acquired_before: Filter for assets with image acquisition before the datetime or isoformat string e.g.
                "2022-01-30".
            geometry: Filter for assets intersecting the Polygon geometry. One of FeatureCollection, Feature,
                dict (geojson geometry), list (bounds coordinates), GeoDataFrame, shapely.Polygon, shapely.Point.
                All assume EPSG 4326!
            custom_filter: A CQL2 filter expression for filtering based on properties, see
                https://pystac-client.readthedocs.io/en/stable/tutorials/cql2-filter.html#CQL2-Filters

        Returns:
            Dict of storage STAC results
        """
        stac_search_parameters: Dict[str, Any] = {
            "max_items": 100,
            "limit": 10000,
        }
        if geometry is not None:
            geometry = any_vector_to_fc(vector=geometry)
            geometry = fc_to_query_geometry(
                fc=geometry, geometry_operation="intersects"
            )
            stac_search_parameters["intersects"] = geometry
        if custom_filter is not None:
            # e.g. {"op": "gte","args": [{"property": "eo:cloud_cover"}, 10]}
            stac_search_parameters["filter"] = custom_filter

        datetime_filter = None
        if acquired_after is not None:
            datetime_filter = f"{format_time(acquired_after)}/.."
        if acquired_before is not None:
            datetime_filter = f"../{format_time(acquired_before)}"
        if acquired_after is not None and acquired_before is not None:
            datetime_filter = (
                f"{format_time(acquired_after)}/{format_time(acquired_before)}"
            )
        stac_search_parameters["datetime"] = datetime_filter  # type: ignore

        url = f"{self.auth._endpoint()}/v2/assets/stac/search"
        # TODO query pagination in separate PR
        stac_results = self.auth._request(
            request_type="POST", url=url, data=stac_search_parameters
        )

        features = stac_results["features"]

        link_elements = [link["body"]["token"] for link in stac_results["links"] if
                         link["rel"] == "next"]

        if len(link_elements) > 0:
            stac_search_parameters["token"] = link_elements[0]
            stac_results = self.auth._request(
                request_type="POST", url=url, data=stac_search_parameters
            )
            features.append(stac_results["features"])

        return features

    def get_assets(
        self,
        created_after: Optional[Union[str, datetime]] = None,
        created_before: Optional[Union[str, datetime]] = None,
        acquired_after: Optional[Union[str, datetime]] = None,
        acquired_before: Optional[Union[str, datetime]] = None,
        geometry: Optional[
            Union[dict, Feature, FeatureCollection, list, GeoDataFrame, Polygon]
        ] = None,
        workspace_id: Optional[str] = None,
        collection_names: List[str] = None,
        producer_names: List[str] = None,
        tags: List[str] = None,
        sources: List[str] = None,
        search: str = None,
        custom_filter: dict = None,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
        return_json: bool = False,
    ) -> Union[List[Asset], dict]:
        """
        Gets all assets in all the accessible workspaces as Asset objects or json.

        Args:
            created_after: Filter for assets created after the datetime or isoformat string e.g. "2022-01-01".
            created_before: Filter for assets created before the datetime or isoformat string e.g. "2022-01-30".
            acquired_after: Filter for assets with image acquisition after the datetime or isoformat string e.g.
                "2022-01-01".
            acquired_before: Filter for assets with image acquisition before the datetime or isoformat string e.g.
                "2022-01-30".
            geometry: Filter for assets intersecting the Polygon geometry. One of FeatureCollection, Feature,
                dict (geojson geometry), list (bounds coordinates), GeoDataFrame, shapely.Polygon, shapely.Point.
                All assume EPSG 4326!
            workspace_id: Filter for assets by the workspace ID. You can use `storage.workspace_id` here
                to limit to your own workspace.
            collection_names: Filter for assets with any of the provided collection names, e.g. ["spot", "phr"].
            producer_names: Filter for assets with any of the provided producer names, e.g. ["airbus", "21at"].
            tags: Filter for assets with any of the provided tags, e.g. ["optical", "US"].
            sources: Filter for assets with any of the provided sources, one or multiple of
                ["ARCHIVE", "TASKING", "ANALYTICSPLATFORM", "USER"].
            search: Filter for assets that contain the provided search query in their name, title, or order ID, e.g.
                "SPOT 6/7 NY Central Park".
            custom_filter: A CQL2 filter expression for filtering based on properties, see
                https://pystac-client.readthedocs.io/en/stable/tutorials/cql2-filter.html#CQL2-Filters
            limit: Optional, only return n first assets (by sorting and order criteria). Optimal to use if your
                workspace contains many assets.
            sortby: The sorting criteria, corresponds to the asset properties, e.g. "created_after".
            descending: The sorting order, True for descending (default), False for ascending.
            return_json: If set to True, returns json dict instead.

        Returns:
            List of asset objects.
        """
        sort = f"{sortby},{'desc' if descending else 'asc'}"
        url = f"{self.auth._endpoint()}/v2/assets?sort={sort}"
        if created_before is not None:
            url += f"&createdBefore={format_time(created_before)}"
        if created_after is not None:
            url += f"&createdAfter={format_time(created_after)}"
        if workspace_id is not None:
            url += f"&workspaceId={workspace_id}"
        if collection_names is not None:
            url += f"&collectionNames={collection_names}"
        if producer_names is not None:
            url += f"&producerNames={producer_names}"
        if tags is not None:
            url += f"&tags={tags}"
        if sources is not None:
            url += f"&sources={sources}"
        if search is not None:
            url += f"&search={search}"

        assets_json = self._query_paginated(url=url, limit=limit)

        # Comparison of asset results with storage stac search results which can be related to the assets via asset-id
        if (
            acquired_before is not None
            or acquired_after is not None
            or geometry is not None
            or custom_filter is not None
        ):
            stac_features = self._search_stac(
                acquired_after=acquired_after,
                acquired_before=acquired_before,
                geometry=geometry,
                custom_filter=custom_filter,
            )
            stac_assets_ids = [
                feature["properties"]["up42-system:asset_id"]
                for feature in stac_features
            ]
            assets_json = [
                asset_json
                for asset_json in assets_json
                if asset_json["id"] in stac_assets_ids
            ]

        if workspace_id is not None:
            logger.info(
                f"Queried {len(assets_json)} assets for workspace {self.workspace_id}."
            )
        else:
            logger.info(
                f"Queried {len(assets_json)} assets from all workspaces in account."
            )

        if return_json:
            return assets_json  # type: ignore
        else:
            assets = [
                Asset(self.auth, asset_id=asset_json["id"], asset_info=asset_json)
                for asset_json in assets_json
            ]
            return assets

    def get_orders(
        self,
        return_json: bool = False,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> Union[List[Order], dict]:
        """
        Gets all orders in the workspace as Order objects or json.

        Args:
            return_json: If set to True, returns json object.
            limit: Optional, only return n first assets by sorting criteria and order.
                Optimal to select if your workspace contains many assets.
            sortby: The sorting criteria, one of "createdAt", "updatedAt", "status", "dataProvider", "type".
            descending: The sorting order, True for descending (default), False for ascending.

        Returns:
            Order objects in the workspace or alternatively json info of the orders.
        """
        allowed_sorting_criteria = [
            "createdAt",
            "updatedAt",
            "type",
            "status",
            "dataProvider",
        ]
        if sortby not in allowed_sorting_criteria:
            raise ValueError(
                f"sortby parameter must be one of {allowed_sorting_criteria}!"
            )
        sort = f"{sortby},{'desc' if descending else 'asc'}"
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders?format=paginated&sort={sort}"
        orders_json = self._query_paginated(url=url, limit=limit)
        logger.info(f"Got {len(orders_json)} orders for workspace {self.workspace_id}.")

        if return_json:
            return orders_json  # type: ignore
        else:
            orders = [
                Order(self.auth, order_id=order_json["id"], order_info=order_json)
                for order_json in orders_json
            ]
            return orders
