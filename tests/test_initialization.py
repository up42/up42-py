import pytest

import up42
from up42 import asset, catalog, job, jobcollection, main, order, project, storage, tasking, workflow

from .fixtures import fixtures_globals as constants


def test_initialize_object_without_auth_raises():
    main._auth = None

    with pytest.raises(RuntimeError):
        up42.initialization.initialize_project()
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_workflow(workflow_id=constants.WORKFLOW_ID)
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_job(job_id=constants.JOB_ID)
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_jobtask(job_id=constants.JOB_ID, jobtask_id=constants.JOBTASK_ID)
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_jobcollection(job_ids=[constants.JOB_ID, constants.JOB_ID])
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_storage()
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_order(order_id=constants.ORDER_ID)
    with pytest.raises(RuntimeError):
        up42.initialization.initialize_asset(asset_id=constants.ASSET_ID)


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
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
        authenticate=True,
        get_info=False,
        retry=False,
    )
    up42_project = up42.initialization.initialize_project()
    assert isinstance(up42_project, project.Project)
    up42_catalog = up42.initialization.initialize_catalog()
    assert isinstance(up42_catalog, catalog.Catalog)
    up42_workflow = up42.initialization.initialize_workflow(workflow_id=constants.WORKFLOW_ID)
    assert isinstance(up42_workflow, workflow.Workflow)
    up42_job = up42.initialization.initialize_job(job_id=constants.JOB_ID)
    assert isinstance(up42_job, job.Job)
    up42_jobtask = up42.initialization.initialize_jobtask(job_id=constants.JOB_ID, jobtask_id=constants.JOBTASK_ID)
    assert isinstance(up42_jobtask, job.JobTask)
    up42_jobcollection = up42.initialization.initialize_jobcollection(job_ids=[constants.JOB_ID, constants.JOB_ID])
    assert isinstance(up42_jobcollection, jobcollection.JobCollection)
    up42_storage = up42.initialization.initialize_storage()
    assert isinstance(up42_storage, storage.Storage)
    up42_order = up42.initialization.initialize_order(order_id=constants.ORDER_ID)
    assert isinstance(up42_order, order.Order)
    up42_asset = up42.initialization.initialize_asset(asset_id=constants.ASSET_ID)
    assert isinstance(up42_asset, asset.Asset)


def test_should_initialize_project_with_project_id(auth_mock, requests_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_project_info = f"{constants.API_HOST}/projects/{project_id}"
    json_project_info = {
        "data": {
            "name": "name",
            "description": "description",
            "createdAt": "date",
        },
    }
    requests_mock.get(url=url_project_info, json=json_project_info)
    project = up42.initialization.initialize_project(project_id=project_id)
    assert project.project_id == project_id


def test_should_initialize_project_with_implicit_project_id(auth_mock, project_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project = up42.initialization.initialize_project()
    assert project.project_id == constants.PROJECT_ID


def test_should_initialize_workflow(auth_mock, requests_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_workflow_info = f"{constants.API_HOST}/projects/{project_id}/workflows/{constants.WORKFLOW_ID}"
    json_workflow_info = {
        "data": {
            "name": "name",
            "id": constants.WORKFLOW_ID,
            "description": "description",
            "createdAt": "date",
        },
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)
    workflow = up42.initialization.initialize_workflow(constants.WORKFLOW_ID, project_id)
    assert workflow.project_id == project_id


def test_should_initialize_workflow_with_implicit_project_id(auth_mock, workflow_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    workflow = up42.initialization.initialize_workflow(constants.WORKFLOW_ID)
    assert workflow.project_id == constants.PROJECT_ID


def test_should_initialize_job(auth_mock, requests_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_job_info = f"{constants.API_HOST}/projects/{project_id}/jobs/{constants.JOB_ID}"
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
    job = up42.initialization.initialize_job(constants.JOB_ID, project_id)
    assert job.project_id == project_id


def test_should_initialize_job_with_implicit_project_id(auth_mock, job_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    job = up42.initialization.initialize_job(constants.JOB_ID)
    assert job.project_id == constants.PROJECT_ID


def test_should_initialize_jobtask(auth_mock, requests_mock, jobtask_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_jobtask_info = f"{constants.API_HOST}/projects/{project_id}/jobs/{constants.JOB_ID}/tasks/"
    requests_mock.get(
        url=url_jobtask_info,
        json={
            "data": [
                {
                    "id": constants.JOBTASK_ID,
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
    job = up42.initialization.initialize_jobtask(constants.JOBTASK_ID, constants.JOB_ID, project_id)
    assert job.project_id == project_id


def test_should_initialize_job_task_with_implicit_project_id(auth_mock, jobtask_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    job = up42.initialization.initialize_jobtask(constants.JOBTASK_ID, constants.JOB_ID)
    assert job.project_id == constants.PROJECT_ID


def test_should_initialize_job_collection(auth_mock, requests_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project_id = "project_id"
    url_job_info = f"{constants.API_HOST}/projects/{project_id}/jobs/{constants.JOB_ID}"
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
    collection = up42.initialization.initialize_jobcollection([constants.JOB_ID], project_id)
    assert all(job.project_id == project_id for job in collection.jobs)
    assert collection.project_id == project_id


def test_should_initialize_job_collection_with_implicit_project_id(auth_mock, job_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    collection = up42.initialization.initialize_jobcollection([constants.JOB_ID])
    assert all(job.project_id == constants.PROJECT_ID for job in collection.jobs)
    assert collection.project_id == constants.PROJECT_ID


def test_should_initialize_tasking(auth_mock):
    up42.main.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    result = up42.initialization.initialize_tasking()
    assert isinstance(result, tasking.Tasking)
