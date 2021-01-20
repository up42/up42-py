from __future__ import absolute_import

import pytest

# pylint: disable=unused-import
from .context import (
    authenticate,
    initialize_project,
    initialize_catalog,
    initialize_workflow,
    initialize_job,
    initialize_jobtask,
    initialize_storage,
    initialize_order,
    initialize_asset,
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


def test_initialize_object_wo_auth_raises():
    with pytest.raises(RuntimeError):
        up42.initialize_project()
    with pytest.raises(RuntimeError):
        up42.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialize_workflow(workflow_id=WORKFLOW_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_job(job_id=JOB_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_jobcollection(job_ids=[JOB_ID, JOB_ID])
    with pytest.raises(RuntimeError):
        up42.initialize_storage()
    with pytest.raises(RuntimeError):
        up42.initialize_order(order_id=ORDER_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_asset(asset_id=ASSET_ID)


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
    project = up42.initialize_project()
    assert isinstance(project, up42.Project)
    catalog = up42.initialize_catalog()
    assert isinstance(catalog, up42.Catalog)
    workflow = up42.initialize_workflow(workflow_id=WORKFLOW_ID)
    assert isinstance(workflow, up42.Workflow)
    job = up42.initialize_job(job_id=JOB_ID)
    assert isinstance(job, up42.Job)
    jobtask = up42.initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)
    assert isinstance(jobtask, up42.JobTask)
    jobcollection = up42.initialize_jobcollection(job_ids=[JOB_ID, JOB_ID])
    assert isinstance(jobcollection, up42.JobCollection)
    storage = up42.initialize_storage()
    assert isinstance(storage, up42.Storage)
    order = up42.initialize_order(order_id=ORDER_ID)
    assert isinstance(order, up42.Order)
    asset = up42.initialize_asset(asset_id=ASSET_ID)
    assert isinstance(asset, up42.Asset)
