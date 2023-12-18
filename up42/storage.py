from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from urllib.parse import urlencode, urljoin
from warnings import warn

from geojson import Feature, FeatureCollection
from geopandas import GeoDataFrame
from shapely.geometry import Polygon

from up42.asset import Asset
from up42.asset_searcher import AssetSearchParams, query_paginated_endpoints, search_assets
from up42.auth import Auth
from up42.order import Order
from up42.stac_client import PySTACAuthClient
from up42.utils import format_time, get_logger

logger = get_logger(__name__)


class AllowedStatuses(Enum):
    CREATED = "CREATED"
    BEING_PLACED = "BEING_PLACED"
    PLACED = "PLACED"
    PLACEMENT_FAILED = "PLACEMENT_FAILED"
    DELIVERY_INITIALIZATION_FAILED = "DELIVERY_INITIALIZATION_FAILED"
    BEING_FULFILLED = "BEING_FULFILLED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    DOWNLOADED = "DOWNLOADED"
    FULFILLED = "FULFILLED"
    FAILED_PERMANENTLY = "FAILED_PERMANENTLY"


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

    @property
    def pystac_client(self):
        url = f"{self.auth._endpoint()}/v2/assets/stac"
        pystac_client_auth = PySTACAuthClient(auth=self.auth).open(url=url)
        return pystac_client_auth

    def _query_paginated_stac_search(
        self,
        url: str,
        stac_search_parameters: dict,
    ) -> list:
        """
        Helper to fetch list of items in paginated stac search endpoind, e.g. stac search assets.

        Args:
            url (str): The base url for paginated endpoint.
            stac_search_parameters (dict): the parameters required for stac search

        Returns:
            List of storage STAC results features.
        """
        response_features: list = []
        response_features_limit = stac_search_parameters["limit"]
        while len(response_features) < response_features_limit:
            stac_results = self.auth._request(request_type="POST", url=url, data=stac_search_parameters)
            response_features.extend(stac_results["features"])
            token_list = [link["body"]["token"] for link in stac_results["links"] if link["rel"] == "next"]
            if token_list:
                stac_search_parameters["token"] = token_list[0]
            else:
                break
        return response_features

    def get_assets(
        self,
        created_after: Optional[Union[str, datetime]] = None,
        created_before: Optional[Union[str, datetime]] = None,
        acquired_after: Optional[Union[str, datetime]] = None,
        acquired_before: Optional[Union[str, datetime]] = None,
        geometry: Optional[Union[dict, Feature, FeatureCollection, list, GeoDataFrame, Polygon]] = None,
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
    ) -> Union[List[Asset], List[dict]]:
        """
        Gets a list of assets in storage as [Asset](https://sdk.up42.com/structure/#asset) objects or in JSON format.

        Args:
            created_after: Search for assets created after the specified timestamp, in `"YYYY-MM-DD"` format.
            created_before: Search for assets created before the specified timestamp, in `"YYYY-MM-DD"` format.
            acquired_after: Deprecated filter.
            acquired_before: Deprecated filter.
            geometry: Deprecated filter.
            workspace_id: Search by the workspace ID.
            collection_names: Search for assets from any of the provided geospatial collections.
            producer_names: Search for assets from any of the provided producers.
            tags: Search for assets with any of the provided tags.
            sources: Search for assets from any of the provided sources.\
                The allowed values: `"ARCHIVE"`, `"TASKING"`, `"USER"`.
            search: Search for assets that contain the provided search query in their name, title, or order ID.
            custom_filter: Deprecated filter.
            limit: The number of results on a results page.
            sortby: The property to sort by.
            descending: The sorting order: <ul><li>`true` — descending</li><li>`false` — ascending</li></ul>
            return_json: If `true`, returns a JSON dictionary.\
                If `false`, returns a list of [Asset](https://sdk.up42.com/structure/#functionality_1) objects.

        Returns:
            A list of Asset objects.
        """
        params: AssetSearchParams = {
            "createdAfter": created_after and format_time(created_after),
            "createdBefore": created_before and format_time(created_before),
            "workspaceId": workspace_id,
            "collectionNames": collection_names,
            "producerNames": producer_names,
            "tags": tags,
            "sources": sources,
            "search": search,
        }
        assets_json = search_assets(
            self.auth,
            params=params,
            limit=limit,
            sortby=sortby,
            descending=descending,
        )

        if (
            acquired_before is not None
            or acquired_after is not None
            or geometry is not None
            or custom_filter is not None
        ):
            warn(
                "Search for geometry, acquired_before, acquired_after and custom_filter has been deprecated."
                "Use the PySTAC client for STAC queries: https://sdk.up42.com/notebooks/stac-example/#pystac",
                DeprecationWarning,
                stacklevel=2,
            )
            raise ValueError(
                "Search for geometry, acquired_before, acquired_after and custom_filter is no longer supported."
            )

        if return_json:
            return assets_json
        else:
            return [Asset(self.auth, asset_id=asset_json["id"], asset_info=asset_json) for asset_json in assets_json]

    def get_orders(
        self,
        workspace_orders: bool = True,
        return_json: bool = False,
        limit: Optional[int] = None,
        sortby: str = "createdAt",
        descending: bool = True,
        order_type: Optional[str] = None,
        statuses: Optional[List[AllowedStatuses]] = None,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[List[Order], List[dict]]:
        """
        Gets all orders in the account/workspace as Order objects or JSON.

        Args:
            workspace_orders: If set to True, only returns workspace orders. Otherwise, returns all account orders.
            return_json: If set to True, returns JSON object.
            limit: Optional, only return n first assets by sorting criteria and order.
                Optimal to select if your workspace contains many assets.
            sortby: The sorting criteria, one of "createdAt", "updatedAt", "status", "dataProvider", "type".
            descending: The sorting order, True for descending (default), False for ascending.
            order_type: Can be either "TASKING" or "ARCHIVE". Pass this param to filter orders based on order_type.
            statuses: Search for orders with any of the statuses provided.
            name: Search for orders that contain this string in their name.
            tags: Search for orders with any of the provided tags.

        Returns:
            Order objects in the workspace or alternatively JSON info of the orders.
        """
        allowed_statuses = {entry.value for entry in AllowedStatuses}

        allowed_sorting_criteria = {
            "createdAt",
            "updatedAt",
            "type",
            "status",
        }
        if sortby not in allowed_sorting_criteria:
            raise ValueError(f"sortby parameter must be one of {allowed_sorting_criteria}!")
        sort = f"{sortby},{'desc' if descending else 'asc'}"
        base_url = f"{self.auth._endpoint()}/v2/orders"

        params = {
            "sort": sort,
            "workspaceId": self.workspace_id if workspace_orders else None,
            "displayName": name,
            "type": order_type if order_type in ["TASKING", "ARCHIVE"] else None,
            "tags": tags,
            "status": set(statuses) & allowed_statuses if statuses else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        if statuses is not None and len(statuses) > len(params["status"]):
            logger.info(
                "statuses not included in allowed_statuses"
                f"{set(statuses).difference(allowed_statuses)} were ignored."
            )

        url = urljoin(base_url, "?" + urlencode(params, doseq=True, safe=""))

        orders_json = query_paginated_endpoints(auth=self.auth, url=url, limit=limit)
        logger_message = f"Got {len(orders_json)} orders" + (
            f" for workspace {self.workspace_id}." if workspace_orders else ""
        )
        logger.info(logger_message)

        if return_json:
            return orders_json
        else:
            return [Order(self.auth, order_id=order_json["id"], order_info=order_json) for order_json in orders_json]
