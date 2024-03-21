import datetime as dt
import math
from typing import Any, Dict, List, Optional, TypedDict, Union
from urllib import parse

from up42 import host, utils

logger = utils.get_logger(__name__)


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

    first_page_response = auth.request(request_type="GET", url=url)
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
        response_json = auth.request(request_type="GET", url=url + f"&page={page}")
        if "data" in response_json:
            response_json = response_json["data"]
        results_list += response_json["content"]
    return results_list[:limit]


class AssetSearchParams(TypedDict, total=False):
    createdAfter: Optional[Union[str, dt.datetime]]  # pylint: disable=invalid-name
    createdBefore: Optional[Union[str, dt.datetime]]  # pylint: disable=invalid-name
    workspaceId: Optional[str]  # pylint: disable=invalid-name
    collectionNames: Optional[List[str]]  # pylint: disable=invalid-name
    producerNames: Optional[List[str]]  # pylint: disable=invalid-name
    tags: Optional[List[str]]
    sources: Optional[List[str]]
    search: Optional[str]


def search_assets(
    auth,
    params: AssetSearchParams,
    limit: Optional[int] = None,
    sortby: str = "createdAt",
    descending: bool = True,
) -> List[dict]:
    """
    Get a list of assets based on specified search parameters.

    Args:
        auth: An instance of the authentication class.
        params: A dictionary containing search parameters defined by the `AssetSearchParams` TypedDict.
        limit: The number of results on a results page (default is `None`).
        sortby: The property to sort the results by (default is "createdAt").
        descending: The sorting order, where `True` is descending and `False` is ascending (default is `True`).

    Returns:
        A list of assets metadata as dictionaries.
    """
    sort = f"""{sortby},{"desc" if descending else "asc"}"""
    request_params: Dict[str, Any] = {"sort": sort}
    request_params.update({key: value for key, value in params.items() if value is not None})
    base_url = host.endpoint("/v2/assets")
    url = parse.urljoin(base_url, "?" + parse.urlencode(request_params, doseq=True, safe=""))
    assets_json = query_paginated_endpoints(auth, url=url, limit=limit)

    if "workspace_id" in request_params:
        logger.info("Queried %s assets for workspace %s.", len(assets_json), auth.workspace_id)
    else:
        logger.info("Queried %s assets from all workspaces in account.", {len(assets_json)})
    return assets_json
