"""
    `up42` is the base library module imported to Python. It provides the elementary
    functionality that is not bound to a specific class of the UP42 structure.
    From `up42` you can also initialize other classes, e.g. for using the catalog, storage etc.

    To import the UP42 library:
    ```python
    import up42
    ```

    Authenticate with UP42:
        https://sdk.up42.com/authentication/.

    To initialize any lower level functionality use e.g.
    ```python
    catalog = up42.initialize_catalog()
    ```
"""

import functools
import warnings
from typing import Callable, Type, Union, cast

import requests
from packaging import version
from requests import exceptions

# pylint: disable=only-importing-modules-is-allowed
from up42.asset import Asset, AssetSorting
from up42.base import authenticate, get_credits_balance, stac_client
from up42.catalog import Catalog
from up42.glossary import CollectionSorting, CollectionType, ProductGlossary
from up42.initialization import (
    initialize_asset,
    initialize_catalog,
    initialize_order,
    initialize_storage,
    initialize_tasking,
)
from up42.order import Order, OrderSorting
from up42.order_template import BatchOrderTemplate
from up42.processing import Job, JobSorting, JobStatus
from up42.stac import extend as stac_extend
from up42.storage import Storage
from up42.tasking import FeasibilityStudy, FeasibilityStudySorting, Quotation, QuotationSorting, Tasking
from up42.tools import get_example_aoi, read_vector_file
from up42.utils import get_up42_py_version
from up42.webhooks import Webhook

stac_extend()

__version__ = get_up42_py_version()


@functools.lru_cache
def _get_latest_version():
    response = requests.get("https://pypi.org/pypi/up42-py/json", timeout=2)
    response.raise_for_status()
    return version.parse(response.json()["info"]["version"])


def _check_version():
    try:
        installed_version = version.parse(__version__)
        latest_version = _get_latest_version()
        if installed_version < latest_version:
            message = f"You're using an outdated version of the UP42 Python SDK: v{installed_version}. A newer version is available: v{latest_version}.\nPlease upgrade to the latest version using **pip install --upgrade up42-py** or conda **conda update -c conda-forge up42-py**."  # pylint: disable=line-too-long # noqa: E501
            warnings.warn(message)
    except exceptions.HTTPError:
        pass


_check_version()

__all__ = [
    cast(
        Union[Type, Callable],
        obj,
    ).__name__
    for obj in [
        Asset,
        AssetSorting,
        Catalog,
        Order,
        OrderSorting,
        Storage,
        Tasking,
        Webhook,
        get_example_aoi,
        read_vector_file,
        initialize_catalog,
        initialize_tasking,
        initialize_storage,
        initialize_order,
        initialize_asset,
        authenticate,
        get_credits_balance,
        stac_client,
        Job,
        JobSorting,
        JobStatus,
        CollectionSorting,
        CollectionType,
        ProductGlossary,
        BatchOrderTemplate,
        Quotation,
        QuotationSorting,
        FeasibilityStudy,
        FeasibilityStudySorting,
    ]
]
