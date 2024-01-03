import pytest

# pylint: disable=wrong-import-order
import up42

# pylint: disable=unused-import
from up42.asset import Asset
from up42.catalog import Catalog
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.jobtask import JobTask
from up42.order import Order
from up42.project import Project
from up42.storage import Storage
from up42.workflow import Workflow

from .fixtures.fixtures_globals import (
    API_HOST,
    ASSET_ID,
    JOB_ID,
    JOBTASK_ID,
    ORDER_ID,
    PROJECT_APIKEY,
    PROJECT_ID,
    WORKFLOW_ID,
)


def test_initialize_object_without_auth_raises():
    up42.main._auth = None

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
    assert isinstance(project, Project)
    catalog = up42.initialize_catalog()
    assert isinstance(catalog, Catalog)
    workflow = up42.initialize_workflow(workflow_id=WORKFLOW_ID)
    assert isinstance(workflow, Workflow)
    job = up42.initialize_job(job_id=JOB_ID)
    assert isinstance(job, Job)
    jobtask = up42.initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)
    assert isinstance(jobtask, JobTask)
    jobcollection = up42.initialize_jobcollection(job_ids=[JOB_ID, JOB_ID])
    assert isinstance(jobcollection, JobCollection)
    storage = up42.initialize_storage()
    assert isinstance(storage, Storage)
    order = up42.initialize_order(order_id=ORDER_ID)
    assert isinstance(order, Order)
    asset = up42.initialize_asset(asset_id=ASSET_ID)
    assert isinstance(asset, Asset)


def test_should_initialize_project_with_project_id(auth_mock, requests_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_project_info = f"{API_HOST}/projects/{project_id}"
    json_project_info = {
        "data": {
            "name": "name",
            "description": "description",
            "createdAt": "date",
        },
    }
    requests_mock.get(url=url_project_info, json=json_project_info)
    project = up42.initialize_project(project_id=project_id)
    assert project.project_id == project_id


def test_should_initialize_project_with_implicit_project_id(auth_mock, project_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    project = up42.initialize_project()
    assert project.project_id == PROJECT_ID


def test_should_initialize_workflow(auth_mock, requests_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_workflow_info = f"{API_HOST}/projects/{project_id}/workflows/{WORKFLOW_ID}"
    json_workflow_info = {
        "data": {
            "name": "name",
            "id": WORKFLOW_ID,
            "description": "description",
            "createdAt": "date",
        },
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)
    workflow = up42.initialize_workflow(WORKFLOW_ID, project_id)
    assert workflow.project_id == project_id


def test_should_initialize_workflow_with_implicit_project_id(auth_mock, workflow_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    workflow = up42.initialize_workflow(WORKFLOW_ID)
    assert workflow.project_id == PROJECT_ID


def test_should_initialize_job(auth_mock, requests_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_job_info = f"{API_HOST}/projects/{project_id}/jobs/{JOB_ID}"
    json_job_info = {
        "data": {
            "mode": "DEFAULT",
            "description": "description",
            "startedAt": "date",
            "workflowName": "workflow_name",
            "name": "name",
            "finishedAt": "date",
            "status": "SUCCESSFUL",
            "inputs": "inputs",
        },
    }
    requests_mock.get(url=url_job_info, json=json_job_info)
    job = up42.initialize_job(JOB_ID, project_id)
    assert job.project_id == project_id


def test_should_initialize_job_with_implicit_project_id(auth_mock, job_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    job = up42.initialize_job(JOB_ID)
    assert job.project_id == PROJECT_ID


def test_should_initialize_jobtask(auth_mock, requests_mock, jobtask_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_jobtask_info = f"{API_HOST}/projects/{project_id}/jobs/{JOB_ID}/tasks/"
    requests_mock.get(
        url=url_jobtask_info,
        json={
            "data": [
                {
                    "id": JOBTASK_ID,
                    "xyz": 789,
                    "name": "name",
                    "status": "SUCCESSFUL",
                    "startedAt": "date",
                    "finishedAt": "date",
                    "block": {"name": "a_block"},
                    "blockVersion": "1.0.0",
                }
            ]
        },
    )
    job = up42.initialize_jobtask(JOBTASK_ID, JOB_ID, project_id)
    assert job.project_id == project_id


def test_should_initialize_job_task_with_implicit_project_id(auth_mock, jobtask_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    job = up42.initialize_jobtask(JOBTASK_ID, JOB_ID)
    assert job.project_id == PROJECT_ID


def test_should_initialize_job_collection(auth_mock, requests_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_job_info = f"{API_HOST}/projects/{project_id}/jobs/{JOB_ID}"
    json_job_info = {
        "data": {
            "mode": "DEFAULT",
            "description": "description",
            "startedAt": "date",
            "workflowName": "workflow_name",
            "name": "name",
            "finishedAt": "date",
            "status": "SUCCESSFUL",
            "inputs": "inputs",
        },
    }
    requests_mock.get(url=url_job_info, json=json_job_info)
    collection = up42.initialize_jobcollection([JOB_ID], project_id)
    assert all(job.project_id == project_id for job in collection.jobs)
    assert collection.project_id == project_id


def test_should_initialize_job_collection_with_implicit_project_id(auth_mock, job_mock):
    up42.authenticate(
        project_id=PROJECT_ID,
        authenticate=False,
    )
    collection = up42.initialize_jobcollection([JOB_ID])
    assert all(job.project_id == PROJECT_ID for job in collection.jobs)
    assert collection.project_id == PROJECT_ID
