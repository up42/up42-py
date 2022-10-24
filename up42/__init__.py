"""
    `up42` is the base library module imported to Python. It provides the elementary
    functionality that is not bound to a specific class of the UP42 structure (Project > Workflow > Job etc.).
    From `up42` you can initialize other existing objects, get information about UP42 data &
    processing blocks, read or draw vector data, and adjust the SDK settings.

    To import the UP42 library:
    ```python
    import up42
    ```
"""

import warnings
from pathlib import Path
from typing import Union, Tuple, List, Optional, Dict
import logging
from datetime import datetime
from functools import wraps

from geopandas import GeoDataFrame

# pylint: disable=wrong-import-position
from up42.tools import Tools
from up42.viztools import VizTools
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
from up42.webhooks import Webhooks, Webhook
from up42.utils import get_logger

logger = get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)

_auth: Auth = None  # type: ignore


def _check_auth_init(func, *args, **kwargs):
    """
    Some functionality of the up42 import object can theoretically be used
    before authentication with UP42, so the auth needs to be checked first.
    """
    # pylint: disable=unused-argument
    @wraps(func)  # required for mkdocstrings
    def inner(*args, **kwargs):
        if _auth is None:
            raise RuntimeError("Not authenticated, call up42.authenticate() first")
        return func(*args, **kwargs)

    return inner


def authenticate(
    cfg_file: Union[str, Path] = None,
    project_id: Optional[str] = None,
    project_api_key: Optional[str] = None,
    **kwargs,
):
    global _auth  # pylint: disable=global-statement
    _auth = Auth(
        cfg_file=cfg_file,
        project_id=project_id,
        project_api_key=project_api_key,
        **kwargs,
    )


@_check_auth_init
def initialize_project() -> "Project":
    """
    Returns the correct Project object (has to exist on UP42).
    """
    project = Project(auth=_auth, project_id=str(_auth.project_id))
    logger.info(f"Initialized {project}")
    return project


@_check_auth_init
def initialize_catalog() -> "Catalog":
    """
    Returns a Catalog object for using the catalog search.
    """
    return Catalog(auth=_auth)


@_check_auth_init
def initialize_tasking() -> "Tasking":
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return Tasking(auth=_auth)


@_check_auth_init
def initialize_workflow(workflow_id: str) -> "Workflow":
    """
    Returns a Workflow object (has to exist on UP42).

    Args:
        workflow_id: The UP42 workflow_id
    """
    workflow = Workflow(
        auth=_auth, workflow_id=workflow_id, project_id=str(_auth.project_id)
    )
    logger.info(f"Initialized {workflow}")
    return workflow


@_check_auth_init
def initialize_job(job_id: str) -> "Job":
    """
    Returns a Job object (has to exist on UP42).

    Args:
        job_id: The UP42 job_id
    """
    job = Job(auth=_auth, job_id=job_id, project_id=str(_auth.project_id))
    logger.info(f"Initialized {job}")
    return job


@_check_auth_init
def initialize_jobtask(jobtask_id: str, job_id: str) -> "JobTask":
    """
    Returns a JobTask object (has to exist on UP42).

    Args:
        jobtask_id: The UP42 jobtask_id
        job_id: The UP42 job_id
    """
    jobtask = JobTask(
        auth=_auth,
        jobtask_id=jobtask_id,
        job_id=job_id,
        project_id=str(_auth.project_id),
    )
    logger.info(f"Initialized {jobtask}")
    return jobtask


@_check_auth_init
def initialize_jobcollection(job_ids: List[str]) -> "JobCollection":
    """
    Returns a JobCollection object (the referenced jobs have to exist on UP42).

    Args:
        job_ids: List of UP42 job_ids
    """
    jobs = [
        Job(auth=_auth, job_id=job_id, project_id=str(_auth.project_id))
        for job_id in job_ids
    ]
    jobcollection = JobCollection(
        auth=_auth, project_id=str(_auth.project_id), jobs=jobs
    )
    logger.info(f"Initialized {jobcollection}")
    return jobcollection


@_check_auth_init
def initialize_storage() -> "Storage":
    """
    Returns a Storage object to list orders and assets.
    """
    return Storage(auth=_auth)


@_check_auth_init
def initialize_order(order_id: str) -> "Order":
    """
    Returns an Order object (has to exist on UP42).

    Args:
        order_id: The UP42 order_id
    """
    order = Order(auth=_auth, order_id=order_id)
    logger.info(f"Initialized {order}")
    return order


@_check_auth_init
def initialize_asset(asset_id: str) -> "Asset":
    """
    Returns an Asset object (has to exist on UP42).

    Args:
        asset_id: The UP42 asset_id
    """
    asset = Asset(auth=_auth, asset_id=asset_id)
    logger.info(f"Initialized {asset}")
    return asset


def get_blocks(
    block_type=None,
    basic: bool = True,
    as_dataframe=False,
):
    tools = Tools(auth=_auth)
    return tools.get_blocks(block_type, basic, as_dataframe)


def get_block_details(block_id: str, as_dataframe=False) -> dict:
    tools = Tools(auth=_auth)
    return tools.get_block_details(block_id, as_dataframe)


def get_block_coverage(block_id: str) -> dict:
    tools = Tools(auth=_auth)
    return tools.get_block_coverage(block_id)


def get_credits_balance() -> dict:
    tools = Tools(auth=_auth)
    return tools.get_credits_balance()


def get_credits_history(
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
) -> Dict[str, Union[str, int, Dict]]:
    tools = Tools(auth=_auth)
    return tools.get_credits_history(start_date, end_date)


def validate_manifest(path_or_json: Union[str, Path, dict]) -> dict:
    tools = Tools(auth=_auth)
    return tools.validate_manifest(path_or_json)


def read_vector_file(
    filename: str = "aoi.geojson", as_dataframe: bool = False
) -> Union[Dict, GeoDataFrame]:
    return Tools().read_vector_file(filename, as_dataframe)


def get_example_aoi(
    location: str = "Berlin", as_dataframe: bool = False
) -> Union[Dict, GeoDataFrame]:
    return Tools().get_example_aoi(location, as_dataframe)


def draw_aoi() -> None:
    return VizTools().draw_aoi()


# pylint: disable=duplicate-code
def plot_coverage(
    scenes: GeoDataFrame,
    aoi: GeoDataFrame = None,
    legend_column: str = "sceneId",
    figsize=(12, 16),
) -> None:
    VizTools().plot_coverage(
        scenes=scenes, aoi=aoi, legend_column=legend_column, figsize=figsize
    )


def plot_quicklooks(
    figsize: Tuple[int, int] = (8, 8), filepaths: Optional[list] = None
) -> None:
    VizTools().plot_quicklooks(figsize=figsize, filepaths=filepaths)


def plot_results(
    figsize: Tuple[int, int] = (8, 8),
    filepaths: Union[List[Union[str, Path]], dict] = None,
    titles: List[str] = None,
) -> None:
    VizTools().plot_results(figsize=figsize, filepaths=filepaths, titles=titles)


def settings(log: bool = True) -> None:
    """
    Configures settings about logging etc. when using the up42-py package.

    Args:
        log: Activates/deactivates logging, default True is activated logging.
    """
    if log:
        logger.info(
            "Logging enabled (default) - use up42.settings(log=False) to disable."
        )
    else:
        logger.info("Logging disabled - use up42.settings(log=True) to reactivate.")

    for name in logging.root.manager.loggerDict:
        setattr(logging.getLogger(name), "disabled", not log)


def initialize_webhook(webhook_id: str) -> Webhook:
    """
    Returns a Webhook object (has to exist on UP42).

    Args:
        webhook_id: The UP42 webhook_id
    """
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    webhook = Webhook(auth=_auth, webhook_id=webhook_id)
    logger.info(f"Initialized {webhook}")
    return webhook


def get_webhooks(return_json: bool = False) -> List[Webhook]:
    """
    Gets all registered webhooks for this workspace.

    Args:
        return_json: If true returns the webhooks information as json instead of webhook class objects.

    Returns:
        A list of the registered webhooks for this workspace.
    """
    webhooks = Webhooks(auth=_auth).get_webhooks(return_json=return_json)
    return webhooks


def create_webhook(
    name: str,
    url: str,
    events: List[str],
    active: bool = False,
    secret: Optional[str] = None,
):
    """
    Registers a new webhook in the system.

    Args:
        name: Webhook name
        url: Unique URL where the webhook will send the message (HTTPS required)
        events: List of event types (order status / job task status)
        active: Webhook status.
        secret: String that acts as signature to the https request sent to the url.

    Returns:
        A dict with details of the registered webhook.
    """
    webhook = Webhooks(auth=_auth).create_webhook(
        name=name, url=url, events=events, active=active, secret=secret
    )
    return webhook


def get_webhook_events() -> dict:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    webhook_events = Webhooks(auth=_auth).get_webhook_events()
    return webhook_events
