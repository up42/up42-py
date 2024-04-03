import logging
import warnings
from typing import List, Optional

from up42 import (
    asset,
    catalog,
    job,
    jobcollection,
    jobtask,
    main,
    order,
    project,
    storage,
    tasking,
    utils,
    webhooks,
    workflow,
)

logger = utils.get_logger(__name__, level=logging.INFO)

DEPRECATION_MESSAGE = "after May 15th, 2024, and will be replaced by new processing functionalities."


def _get_project_id(project_id: Optional[str]) -> str:
    if not project_id:
        warnings.warn(
            "Provide the project ID as the value of the `project_id` argument.",
            DeprecationWarning,
            stacklevel=2,
        )
    result = project_id or main.get_auth_safely().project_id
    if not result:
        raise ValueError("Project ID can't be null")
    return result


@main.check_auth
def initialize_project(project_id: Optional[str] = None) -> project.Project:
    """
    Returns the correct Project object (has to exist on UP42).
    Args:
        project_id: The UP42 project id
    """
    warnings.warn(
        "Projects are getting deprecated. The current analytics platform will be discontinued "
        f"{DEPRECATION_MESSAGE}",
        DeprecationWarning,
    )
    up42_project = project.Project(
        auth=main.get_auth_safely(),
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info("Initialized %s", up42_project)
    return up42_project


@main.check_auth
def initialize_catalog() -> catalog.Catalog:
    """
    Returns a Catalog object for using the catalog search.
    """
    return catalog.Catalog(auth=main.get_auth_safely())


@main.check_auth
def initialize_tasking() -> "tasking.Tasking":
    """
    Returns a Tasking object for creating satellite tasking orders.
    """
    return tasking.Tasking(auth=main.get_auth_safely())


@main.check_auth
def initialize_workflow(workflow_id: str, project_id: Optional[str] = None) -> workflow.Workflow:
    """
    Returns a Workflow object (has to exist on UP42).
    Args:
        workflow_id: The UP42 workflow_id
        project_id: The id of the UP42 project, containing the workflow
    """
    warnings.warn(
        "Workflows are getting deprecated. The current analytics platform will be discontinued "
        f"{DEPRECATION_MESSAGE}",
        DeprecationWarning,
    )
    up42_workflow = workflow.Workflow(
        auth=main.get_auth_safely(),
        workflow_id=workflow_id,
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info("Initialized %s", up42_workflow)
    return up42_workflow


@main.check_auth
def initialize_job(job_id: str, project_id: Optional[str] = None) -> job.Job:
    """
    Returns a Job object (has to exist on UP42).
    Args:
        job_id: The UP42 job_id
        project_id: The id of the UP42 project, containing the job
    """
    warnings.warn(
        "Jobs are getting deprecated. The current analytics platform will be discontinued " f"{DEPRECATION_MESSAGE}",
        DeprecationWarning,
    )
    up42_job = job.Job(
        auth=main.get_auth_safely(),
        job_id=job_id,
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info("Initialized %s", up42_job)
    return up42_job


@main.check_auth
def initialize_jobtask(jobtask_id: str, job_id: str, project_id: Optional[str] = None) -> jobtask.JobTask:
    """
    Returns a JobTask object (has to exist on UP42).
    Args:
        jobtask_id: The UP42 jobtask_id
        job_id: The UP42 job_id
        project_id: The id of the UP42 project, containing the job
    """
    warnings.warn(
        "Job tasks are getting deprecated. The current analytics platform will be discontinued "
        f"{DEPRECATION_MESSAGE}",
        DeprecationWarning,
    )
    job_task = jobtask.JobTask(
        auth=main.get_auth_safely(),
        jobtask_id=jobtask_id,
        job_id=job_id,
        project_id=_get_project_id(project_id=project_id),
    )
    logger.info("Initialized %s", job_task)
    return job_task


@main.check_auth
def initialize_jobcollection(job_ids: List[str], project_id: Optional[str] = None) -> jobcollection.JobCollection:
    """
    Returns a JobCollection object (the referenced jobs have to exist on UP42).
    Args:
        job_ids: List of UP42 job_ids
        project_id: The id of the UP42 project, containing the jobs
    """
    warnings.warn(
        "Job Collections are getting deprecated. The current analytics platform will be discontinued "
        f"{DEPRECATION_MESSAGE}",
        DeprecationWarning,
    )
    jobs = [
        job.Job(
            auth=main.get_auth_safely(),
            job_id=job_id,
            project_id=_get_project_id(project_id=project_id),
        )
        for job_id in job_ids
    ]
    job_collection = jobcollection.JobCollection(
        auth=main.get_auth_safely(),
        project_id=_get_project_id(project_id=project_id),
        jobs=jobs,
    )
    logger.info("Initialized %s", job_collection)
    return job_collection


@main.check_auth
def initialize_storage() -> storage.Storage:
    """
    Returns a Storage object to list orders and assets.
    """
    return storage.Storage(auth=main.get_auth_safely())


@main.check_auth
def initialize_order(order_id: str) -> order.Order:
    """
    Returns an Order object (has to exist on UP42).
    Args:
        order_id: The UP42 order_id
    """
    up42_order = order.Order(auth=main.get_auth_safely(), order_id=order_id)
    logger.info("Initialized %s", up42_order)
    return up42_order


@main.check_auth
def initialize_asset(asset_id: str) -> asset.Asset:
    """
    Returns an Asset object (has to exist on UP42).
    Args:
        asset_id: The UP42 asset_id
    """
    up42_asset = asset.Asset(auth=main.get_auth_safely(), asset_id=asset_id)
    logger.info("Initialized %s", up42_asset)
    return up42_asset


@main.check_auth
def initialize_webhook(webhook_id: str) -> webhooks.Webhook:
    """
    Returns a Webhook object (has to exist on UP42).
    Args:
        webhook_id: The UP42 webhook_id
    """
    webhook = webhooks.Webhook(auth=main.get_auth_safely(), webhook_id=webhook_id)
    logger.info("Initialized %s", webhook)
    return webhook
