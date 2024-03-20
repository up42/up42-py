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
    ```python
    project = up42.initialize_project(project_id="your-project-ID")
    ```
"""

# pylint: disable=only-importing-modules-is-allowed
from up42.asset import Asset
from up42.auth import Auth
from up42.catalog import Catalog
from up42.initialization import (
    initialize_asset,
    initialize_catalog,
    initialize_job,
    initialize_jobcollection,
    initialize_jobtask,
    initialize_order,
    initialize_project,
    initialize_storage,
    initialize_tasking,
    initialize_webhook,
    initialize_workflow,
)
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.jobtask import JobTask
from up42.main import (
    authenticate,
    create_webhook,
    get_block_coverage,
    get_block_details,
    get_blocks,
    get_credits_balance,
    get_webhook_events,
    get_webhooks,
)
from up42.order import Order
from up42.project import Project
from up42.storage import Storage
from up42.tasking import Tasking
from up42.tools import get_example_aoi, read_vector_file
from up42.utils import get_up42_py_version
from up42.viztools import draw_aoi
from up42.webhooks import Webhook
from up42.workflow import Workflow

__version__ = get_up42_py_version()

__all__ = [
    obj.__name__
    for obj in [
        Asset,
        Auth,
        Catalog,
        Job,
        JobCollection,
        JobTask,
        Order,
        Project,
        Storage,
        Tasking,
        Webhook,
        Workflow,
        get_example_aoi,
        read_vector_file,
        draw_aoi,
        initialize_project,
        initialize_catalog,
        initialize_tasking,
        initialize_workflow,
        initialize_job,
        initialize_jobtask,
        initialize_jobcollection,
        initialize_storage,
        initialize_order,
        initialize_asset,
        initialize_webhook,
        authenticate,
        get_webhooks,
        create_webhook,
        get_webhook_events,
        get_blocks,
        get_block_details,
        get_block_coverage,
        get_credits_balance,
    ]
]
