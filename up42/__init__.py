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
from up42.asset import Asset, AssetSorting
from up42.base import authenticate, get_credits_balance, stac_client
from up42.catalog import Catalog
from up42.glossary import CollectionSorting, CollectionType, ProductGlossary, Provider
from up42.initialization import initialize_asset, initialize_catalog, initialize_order, initialize_storage
from up42.order import Order, OrderSorting
from up42.order_template import BatchOrderTemplate
from up42.processing import Job, JobSorting, JobStatus
from up42.stac import BulkDeletion
from up42.stac import extend as stac_extend
from up42.storage import Storage
from up42.tasking import FeasibilityStudy, FeasibilityStudySorting, Quotation, QuotationSorting
from up42.tools import get_example_aoi, read_vector_file
from up42.utils import get_up42_py_version
from up42.version import version_control
from up42.webhooks import Webhook

stac_extend()

__version__ = get_up42_py_version()
version_control.check_is_latest_version(__version__)

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
        Webhook,
        get_example_aoi,
        read_vector_file,
        initialize_catalog,
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
        Provider,
        BatchOrderTemplate,
        Quotation,
        QuotationSorting,
        FeasibilityStudy,
        FeasibilityStudySorting,
        BulkDeletion,
    ]
]
