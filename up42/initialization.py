__all__ = [
    "initialize_project",
    "initialize_catalog",
    "initialize_tasking",
    "initialize_workflow",
    "initialize_job",
    "initialize_jobtask",
    "initialize_jobcollection",
    "initialize_storage",
    "initialize_order",
    "initialize_asset",
    "initialize_webhook",
]

import logging
from typing import List, Optional
from warnings import warn

from up42 import main
from up42.asset import Asset
from up42.catalog import Catalog
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.jobtask import JobTask
from up42.main import _check_auth
from up42.order import Order
from up42.project import Project
from up42.storage import Storage
from up42.tasking import Tasking
from up42.utils import get_logger
from up42.webhooks import Webhook
from up42.workflow import Workflow

logger = get_logger(__name__, level=logging.INFO)


def _get_project_id(project_id: Optional[str]) -> str:
    if not project_id:
        warn(
            "Provide the project ID as the value of the `project_id` argument.",
            DeprecationWarning,
            stacklevel=2,
        )
    result = project_id or str(main._auth.project_id)
    if not result:
        raise ValueError("Project ID can't be null")
    return result


@_check_auth
def initialize_project(project_id: Optional[str] = None) -> "Project":
    """
    Returns the correct Project object (has to exist on UP42).
    Args:
        project_id: The UP42 project id
    """
    warn(
        "Projects are getting deprecated. The current analytics platform will be discontinued "
        "after January 31, 2024, and will be replaced by new processing functionalities.",
        DeprecationWarning,
    )
    project = Project(auth=main._auth, project_id=_get_project_id(project_id=project_id))
    logger.info(f"Initialized {project}")
    return project


@_check_auth
def initialize_catalog() -> "Catalog":
    """
    Returns a Catalog object for using the catalog search.
    """
    return Catalog(auth=main._auth)


@_check_auth
def initialize_tasking() -> "Tasking":
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return Tasking(auth=main._auth)


@_check_auth
def initialize_workflow(workflow_id: str, project_id: Optional[str] = None) -> "Workflow":
    """
    Returns a Workflow object (has to exist on UP42).
    Args:
        workflow_id: The UP42 workflow_id
        project_id: The id of the UP42 project, containing the workflow
    """
    warn(
        "Workflows are getting deprecated. The current analytics platform will be discontinued "
        "after January 31, 2024, and will be replaced by new processing functionalities.",
        DeprecationWarning,
    )
    workflow = Workflow(
        auth=main._auth,
        workflow_id=workflow_id,
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info(f"Initialized {workflow}")
    return workflow


@_check_auth
def initialize_job(job_id: str, project_id: Optional[str] = None) -> "Job":
    """
    Returns a Job object (has to exist on UP42).
    Args:
        job_id: The UP42 job_id
        project_id: The id of the UP42 project, containing the job
    """
    warn(
        "Jobs are getting deprecated. The current analytics platform will be discontinued "
        "after January 31, 2024, and will be replaced by new processing functionalities.",
        DeprecationWarning,
    )
    job = Job(
        auth=main._auth,
        job_id=job_id,
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info(f"Initialized {job}")
    return job


@_check_auth
def initialize_jobtask(jobtask_id: str, job_id: str, project_id: Optional[str] = None) -> "JobTask":
    """
    Returns a JobTask object (has to exist on UP42).
    Args:
        jobtask_id: The UP42 jobtask_id
        job_id: The UP42 job_id
        project_id: The id of the UP42 project, containing the job
    """
    warn(
        "Job tasks are getting deprecated. The current analytics platform will be discontinued "
        "after January 31, 2024, and will be replaced by new processing functionalities.",
        DeprecationWarning,
    )
    jobtask = JobTask(
        auth=main._auth,
        jobtask_id=jobtask_id,
        job_id=job_id,
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info(f"Initialized {jobtask}")
    return jobtask


@_check_auth
def initialize_jobcollection(job_ids: List[str], project_id: Optional[str] = None) -> "JobCollection":
    """
    Returns a JobCollection object (the referenced jobs have to exist on UP42).
    Args:
        job_ids: List of UP42 job_ids
        project_id: The id of the UP42 project, containing the jobs
    """
    warn(
        "Job Collections are getting deprecated. The current analytics platform will be discontinued "
        "after January 31, 2024, and will be replaced by new processing functionalities.",
        DeprecationWarning,
    )
    jobs = [
        Job(
            auth=main._auth,
            job_id=job_id,
            project_id=_get_project_id(project_id=project_id),
        )
        for job_id in job_ids
    ]
    jobcollection = JobCollection(
        auth=main._auth,
        project_id=_get_project_id(project_id=project_id),
        jobs=jobs,
    )
    logger.info(f"Initialized {jobcollection}")
    return jobcollection


@_check_auth
def initialize_storage() -> "Storage":
    """
    Returns a Storage object to list orders and assets.
    """
    return Storage(auth=main._auth)


@_check_auth
def initialize_order(order_id: str) -> "Order":
    """
    Returns an Order object (has to exist on UP42).
    Args:
        order_id: The UP42 order_id
    """
    order = Order(auth=main._auth, order_id=order_id)
    logger.info(f"Initialized {order}")
    return order


@_check_auth
def initialize_asset(asset_id: str) -> "Asset":
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    asset = Asset(auth=main._auth, asset_id=asset_id)
    logger.info(f"Initialized {asset}")
    return asset


@_check_auth
def initialize_webhook(webhook_id: str) -> Webhook:
    """
    Returns a Webhook object (has to exist on UP42).
    Args:
        webhook_id: The UP42 webhook_id
    """
    webhook = Webhook(auth=main._auth, webhook_id=webhook_id)
    logger.info(f"Initialized {webhook}")
    return webhook
