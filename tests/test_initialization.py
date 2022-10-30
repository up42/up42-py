import pytest

# pylint: disable=unused-import
from .context import (
    initialize_project,
    initialize_catalog,
    initialize_workflow,
    initialize_job,
    initialize_jobtask,
    initialize_jobcollection,
    initialize_storage,
    initialize_order,
    initialize_asset,
    Project,
    Catalog,
    Workflow,
    Job,
    JobTask,
    JobCollection,
    Storage,
    Order,
    Asset,
)
from .fixtures import (
    PROJECT_ID,
    PROJECT_APIKEY,
    WORKFLOW_ID,
    JOB_ID,
    JOBTASK_ID,
    ORDER_ID,
    ASSET_ID,
    auth_mock,
    project_mock,
    workflow_mock,
    job_mock,
    jobtask_mock,
    jobcollection_single_mock,
    storage_mock,
    order_mock,
    asset_mock,
)
import up42  # pylint: disable=wrong-import-order


def test_initialize_object_without_auth_raises():
    with pytest.raises(RuntimeError):
        initialize_project()
    with pytest.raises(RuntimeError):
        initialize_catalog()
    with pytest.raises(RuntimeError):
        initialize_workflow(workflow_id=WORKFLOW_ID)
    with pytest.raises(RuntimeError):
        initialize_job(job_id=JOB_ID)
    with pytest.raises(RuntimeError):
        initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)
    with pytest.raises(RuntimeError):
        initialize_jobcollection(job_ids=[JOB_ID, JOB_ID])
    with pytest.raises(RuntimeError):
        initialize_storage()
    with pytest.raises(RuntimeError):
        initialize_order(order_id=ORDER_ID)
    with pytest.raises(RuntimeError):
        initialize_asset(asset_id=ASSET_ID)


# pylint: disable=unused-argument
def test_global_auth_initialize_objects(
    auth_mock,
    project_mock,
    workflow_mock,
    job_mock,
    jobtask_mock,
    jobcollection_single_mock,
    storage_mock,
    order_mock,
    asset_mock,
):
    up42.authenticate(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        authenticate=True,
        get_info=False,
        retry=False,
    )
    project = initialize_project()
    assert isinstance(project, Project)
    catalog = initialize_catalog()
    assert isinstance(catalog, Catalog)
    workflow = initialize_workflow(workflow_id=WORKFLOW_ID)
    assert isinstance(workflow, Workflow)
    job = initialize_job(job_id=JOB_ID)
    assert isinstance(job, Job)
    jobtask = initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)
    assert isinstance(jobtask, JobTask)
    jobcollection = initialize_jobcollection(job_ids=[JOB_ID, JOB_ID])
    assert isinstance(jobcollection, JobCollection)
    storage = initialize_storage()
    assert isinstance(storage, Storage)
    order = initialize_order(order_id=ORDER_ID)
    assert isinstance(order, Order)
    asset = initialize_asset(asset_id=ASSET_ID)
    assert isinstance(asset, Asset)
