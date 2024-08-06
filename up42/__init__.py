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

from typing import Callable, Type, Union, cast

# pylint: disable=only-importing-modules-is-allowed
from up42.asset import Asset
from up42.auth import Auth
from up42.base import authenticate, get_credits_balance
from up42.catalog import Catalog
from up42.glossary import CollectionSorting, CollectionType, ProductGlossary
from up42.initialization import (
    initialize_asset,
    initialize_catalog,
    initialize_order,
    initialize_storage,
    initialize_tasking,
)
from up42.order import Order
from up42.processing import Job, JobSorting, JobStatus
from up42.storage import Storage
from up42.tasking import Tasking
from up42.tools import get_example_aoi, read_vector_file
from up42.utils import get_up42_py_version
from up42.webhooks import Webhook

__version__ = get_up42_py_version()
__all__ = [
    cast(
        Union[Type, Callable],
        obj,
    ).__name__
    for obj in [
        Asset,
        Auth,
        Catalog,
        Order,
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
        Job,
        JobSorting,
        JobStatus,
        CollectionSorting,
        CollectionType,
        ProductGlossary,
    ]
]
