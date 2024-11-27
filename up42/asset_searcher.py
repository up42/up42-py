import datetime as dt
from typing import List, Optional, TypedDict, Union

from up42 import utils

logger = utils.get_logger(__name__)


class AssetSearchParams(TypedDict, total=False):
    createdAfter: Optional[Union[str, dt.datetime]]  # pylint: disable=invalid-name
    createdBefore: Optional[Union[str, dt.datetime]]  # pylint: disable=invalid-name
    workspaceId: Optional[str]  # pylint: disable=invalid-name
    collectionNames: Optional[List[str]]  # pylint: disable=invalid-name
    producerNames: Optional[List[str]]  # pylint: disable=invalid-name
    tags: Optional[List[str]]
    sources: Optional[List[str]]
    search: Optional[str]
    sort: utils.SortingField


def search_assets(
    auth,
    params: AssetSearchParams,
    limit: Optional[int] = None,
) -> List[dict]:
    """
    Get a list of assets based on specified search parameters.

    Args:
        auth: An instance of the authentication class.
        params: A dictionary containing search parameters defined by the `AssetSearchParams` TypedDict.
        limit: The number of results on a results page (default is `None`).

    Returns:
        A list of assets metadata as dictionaries.
    """
    return list(utils.query(params, "/v2/assets", auth.session))[:limit]  # type: ignore
