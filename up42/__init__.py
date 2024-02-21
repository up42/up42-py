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


from up42 import initialization, main, tools, utils, viztools, webhooks
from up42.asset import Asset
from up42.auth import Auth
from up42.catalog import Catalog
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.jobtask import JobTask
from up42.order import Order
from up42.project import Project
from up42.storage import Storage
from up42.tasking import Tasking
from up42.workflow import Workflow

__version__ = utils.get_up42_py_version()

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
        webhooks.Webhook,
        Workflow,
        tools.get_example_aoi,
        tools.read_vector_file,
        viztools.draw_aoi,
        initialization.initialize_project,
        initialization.initialize_catalog,
        initialization.initialize_tasking,
        initialization.initialize_workflow,
        initialization.initialize_job,
        initialization.initialize_jobtask,
        initialization.initialize_jobcollection,
        initialization.initialize_storage,
        initialization.initialize_order,
        initialization.initialize_asset,
        initialization.initialize_webhook,
        main.authenticate,
        main.get_webhooks,
        main.create_webhook,
        main.get_webhook_events,
        main.get_blocks,
        main.get_block_details,
        main.get_block_coverage,
        main.get_credits_balance,
    ]
]
