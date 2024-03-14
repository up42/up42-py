import pytest

import up42
from up42 import catalog, main, tasking

from .fixtures import fixtures_globals as constants


def test_initialize_object_without_auth_raises():
    main._auth = None  # pylint: disable=protected-access

    with pytest.raises(RuntimeError):
        up42.initialize_project()
    with pytest.raises(RuntimeError):
        up42.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialize_workflow(workflow_id=constants.WORKFLOW_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_job(job_id=constants.JOB_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_jobtask(job_id=constants.JOB_ID, jobtask_id=constants.JOBTASK_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_jobcollection(job_ids=[constants.JOB_ID, constants.JOB_ID])
    with pytest.raises(RuntimeError):
        up42.initialize_storage()
    with pytest.raises(RuntimeError):
        up42.initialize_order(order_id=constants.ORDER_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_asset(asset_id=constants.ASSET_ID)


def test_global_auth_initialize_objects(
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
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
        authenticate=True,
        get_info=False,
        retry=False,
    )
    project_obj = up42.initialize_project()
    assert project_obj.info == project_mock.info
    catalog_obj = up42.initialize_catalog()
    assert isinstance(catalog_obj, catalog.Catalog)
    workflow_obj = up42.initialize_workflow(workflow_id=constants.WORKFLOW_ID)
    assert workflow_obj.info == workflow_mock.info
    job_obj = up42.initialize_job(job_id=constants.JOB_ID)
    assert job_obj.info == job_mock.info
    jobtask_obj = up42.initialize_jobtask(job_id=constants.JOB_ID, jobtask_id=constants.JOBTASK_ID)
    assert jobtask_obj.info == jobtask_mock.info
    jobcollection_obj = up42.initialize_jobcollection(job_ids=[constants.JOB_ID, constants.JOB_ID])
    assert jobcollection_obj.info == jobcollection_single_mock.info
    storage_obj = up42.initialize_storage()
    assert storage_obj.workspace_id == storage_mock.workspace_id
    order_obj = up42.initialize_order(order_id=constants.ORDER_ID)
    assert order_obj.info == order_mock.info
    asset_obj = up42.initialize_asset(asset_id=constants.ASSET_ID)
    assert asset_obj.info == asset_mock.info


def test_should_initialize_project_with_project_id(requests_mock):
    up42.authenticate(
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
    project_obj = up42.initialize_project(project_id=project_id)
    assert project_obj.project_id == project_id


def test_should_initialize_project_with_implicit_project_id(project_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    project_obj = up42.initialize_project()
    assert project_obj.info == project_mock.info
    assert project_obj.project_id == constants.PROJECT_ID


def test_should_initialize_workflow(requests_mock):
    up42.authenticate(
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
    workflow_obj = up42.initialize_workflow(constants.WORKFLOW_ID, project_id)
    assert workflow_obj.project_id == project_id


def test_should_initialize_workflow_with_implicit_project_id(workflow_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    workflow_obj = up42.initialize_workflow(constants.WORKFLOW_ID)
    assert workflow_obj.info == workflow_mock.info
    assert workflow_obj.project_id == constants.PROJECT_ID


def test_should_initialize_job(requests_mock):
    up42.authenticate(
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
    job_obj = up42.initialize_job(constants.JOB_ID, project_id)
    assert job_obj.project_id == project_id


def test_should_initialize_job_with_implicit_project_id(job_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    job_obj = up42.initialize_job(constants.JOB_ID)
    assert job_obj.info == job_mock.info
    assert job_obj.project_id == constants.PROJECT_ID


def test_should_initialize_jobtask(requests_mock):
    up42.authenticate(
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
    job_obj = up42.initialize_jobtask(constants.JOBTASK_ID, constants.JOB_ID, project_id)
    assert job_obj.project_id == project_id


def test_should_initialize_job_task_with_implicit_project_id(jobtask_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    jobtask_obj = up42.initialize_jobtask(constants.JOBTASK_ID, constants.JOB_ID)
    assert jobtask_obj.info == jobtask_mock.info
    assert jobtask_obj.project_id == constants.PROJECT_ID


def test_should_initialize_job_collection(requests_mock):
    up42.authenticate(
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
    collection = up42.initialize_jobcollection([constants.JOB_ID], project_id)
    assert all(job.project_id == project_id for job in collection.jobs)
    assert collection.project_id == project_id


def test_should_initialize_job_collection_with_implicit_project_id(job_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    collection = up42.initialize_jobcollection([constants.JOB_ID])
    assert collection.jobs[0].info == job_mock.info
    assert all(job.project_id == constants.PROJECT_ID for job in collection.jobs)
    assert collection.project_id == constants.PROJECT_ID


def test_should_initialize_tasking():
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        authenticate=False,
    )
    result = up42.initialize_tasking()
    assert isinstance(result, tasking.Tasking)
