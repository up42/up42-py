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
from typing import List

from up42 import main
from up42.main import _check_auth
from up42.utils import get_logger
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


logger = get_logger(__name__, level=logging.INFO)


@_check_auth
def initialize_project() -> "Project":
    """
    Returns the correct Project object (has to exist on UP42).
    """
    project = Project(auth=main._auth, project_id=str(main._auth.project_id))
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
def initialize_workflow(workflow_id: str) -> "Workflow":
    """
    Returns a Workflow object (has to exist on UP42).
    Args:
        workflow_id: The UP42 workflow_id
    """
    workflow = Workflow(
        auth=main._auth, workflow_id=workflow_id, project_id=str(main._auth.project_id)
    )
    logger.info(f"Initialized {workflow}")
    return workflow


@_check_auth
def initialize_job(job_id: str) -> "Job":
    """
    Returns a Job object (has to exist on UP42).
    Args:
        job_id: The UP42 job_id
    """
    job = Job(auth=main._auth, job_id=job_id, project_id=str(main._auth.project_id))
    logger.info(f"Initialized {job}")
    return job


@_check_auth
def initialize_jobtask(jobtask_id: str, job_id: str) -> "JobTask":
    """
    Returns a JobTask object (has to exist on UP42).
    Args:
        jobtask_id: The UP42 jobtask_id
        job_id: The UP42 job_id
    """
    jobtask = JobTask(
        auth=main._auth,
        jobtask_id=jobtask_id,
        job_id=job_id,
        project_id=str(main._auth.project_id),
    )
    logger.info(f"Initialized {jobtask}")
    return jobtask


@_check_auth
def initialize_jobcollection(job_ids: List[str]) -> "JobCollection":
    """
    Returns a JobCollection object (the referenced jobs have to exist on UP42).
    Args:
        job_ids: List of UP42 job_ids
    """
    jobs = [
        Job(auth=main._auth, job_id=job_id, project_id=str(main._auth.project_id))
        for job_id in job_ids
    ]
    jobcollection = JobCollection(
        auth=main._auth, project_id=str(main._auth.project_id), jobs=jobs
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
