"""
    `up42` is the base library module imported to Python. It provides the elementary
    functionality that is not bound to a specific class of the UP42 structure.
    From `up42` you can also initialize other classes, e.g. for using the catalog, storage etc.

    To import the UP42 library:
    ```python
    import up42
    ```

    Authenticate with UP42 via
    ```python
    up42.authenticate(
        project_id="your-project-ID",
        project_api_key="your-project-API-key"
    )
    ```

    To initialize any lower level functionality use e.g.
    ```python
    catalog = up42.initialize_catalog()
    ```
    ```python
    project = up42.initialize_project()
    ```
"""

from pathlib import Path

from up42.main import *  # defined by __all__
from up42.initialization import *  # defined by __all__
from up42.tools import read_vector_file, get_example_aoi
from up42.viztools import draw_aoi

from up42.auth import Auth
from up42.project import Project
from up42.workflow import Workflow
from up42.job import Job
from up42.jobtask import JobTask
from up42.jobcollection import JobCollection
from up42.catalog import Catalog
from up42.tasking import Tasking
from up42.storage import Storage
from up42.order import Order
from up42.asset import Asset
from up42.webhooks import Webhook


__version__ = (Path(__file__).resolve().parent / "_version.txt").read_text(
    encoding="utf-8"
)
