import math
from datetime import datetime
from typing import List, Optional, TypedDict, Union
from urllib.parse import urlencode, urljoin

from up42.utils import get_logger

logger = get_logger(__name__)


def query_paginated_endpoints(auth, url: str, limit: Optional[int] = None, size: int = 50) -> List[dict]:
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

    first_page_response = auth._request(request_type="GET", url=url)
    if "data" in first_page_response:  # UP42 API v2 convention without data key, but still in e.g. get order
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
        response_json = auth._request(request_type="GET", url=url + f"&page={page}")
        if "data" in response_json:
            response_json = response_json["data"]
        results_list += response_json["content"]
    return results_list[:limit]


class AssetSearchParams(TypedDict):
    createdAfter: Optional[Union[str, datetime]]
    createdBefore: Optional[Union[str, datetime]]
    workspaceId: Optional[str]
    collectionNames: Optional[List[str]]
    producerNames: Optional[List[str]]
    tags: Optional[List[str]]
    sources: Optional[List[str]]
    search: Optional[str]


def asset_search(
    auth,
    params_asset_search: AssetSearchParams,
    limit: Optional[int] = None,
    sortby: str = "createdAt",
    descending: bool = True,
) -> dict:
    """
        Gets a list of assets in storage as [Asset](https://sdk.up42.com/structure/#functionality_1)
        objects or in JSON format.

        Args:
            created_after: Search for assets created after the specified timestamp, in `"YYYY-MM-DD"` format.
            created_before: Search for assets created before the specified timestamp, in `"YYYY-MM-DD"` format.
            workspace_id: Search by the workspace ID.
            collection_names: Search for assets from any of the provided geospatial collections.
            producer_names: Search for assets from any of the provided producers.
            tags: Search for assets with any of the provided tags.
            sources: Search for assets from any of the provided sources.\
                The allowed values: `"ARCHIVE"`, `"TASKING"`, `"USER"`.
            search: Search for assets that contain the provided search query in their name, title, or order ID.
            limit: The number of results on a results page.
            sortby: The property to sort by.
            descending: The sorting order: <ul><li>`true` — descending</li><li>`false` — ascending</li></ul>
            return_json: If `true`, returns a JSON dictionary.\
                If `false`, returns a list of [Asset](https://sdk.up42.com/structure/#functionality_1) objects.

        Returns:
            A list of Asset objects.
        """
    sort = f"{sortby},{'desc' if descending else 'asc'}"
    params = {"sort": sort, **params_asset_search}  # type: ignore[arg-type]
    params = {k: v for k, v in params.items() if v is not None}
    base_url = f"{auth._endpoint()}/v2/assets?sort={sort}"
    url = urljoin(base_url, "?" + urlencode(params, doseq=True, safe=""))
    assets_json = query_paginated_endpoints(auth, url=url, limit=limit)

    if params.get("workspace_id"):
        logger.info(f"Queried {len(assets_json)} assets for workspace {auth.workspace_id}.")
    else:
        logger.info(f"Queried {len(assets_json)} assets from all workspaces in account.")
    return assets_json  # type: ignore
