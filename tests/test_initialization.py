import pytest

import up42
from up42 import catalog, main, tasking

from .fixtures import fixtures_globals as constants


def test_initialize_object_without_auth_raises():
    main._auth = None  # pylint: disable=protected-access

    with pytest.raises(RuntimeError):
        up42.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialize_workflow(workflow_id=constants.WORKFLOW_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_jobtask(job_id=constants.JOB_ID, jobtask_id=constants.JOBTASK_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_storage()
    with pytest.raises(RuntimeError):
        up42.initialize_order(order_id=constants.ORDER_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_asset(asset_id=constants.ASSET_ID)


def test_global_auth_initialize_objects(
    workflow_mock,
    jobtask_mock,
    storage_mock,
    order_mock,
    asset_mock,
):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
    )
    catalog_obj = up42.initialize_catalog()
    assert isinstance(catalog_obj, catalog.Catalog)
    workflow_obj = up42.initialize_workflow(workflow_id=constants.WORKFLOW_ID)
    assert workflow_obj.info == workflow_mock.info
    jobtask_obj = up42.initialize_jobtask(job_id=constants.JOB_ID, jobtask_id=constants.JOBTASK_ID)
    assert jobtask_obj.info == jobtask_mock.info
    storage_obj = up42.initialize_storage()
    assert storage_obj.workspace_id == storage_mock.workspace_id
    order_obj = up42.initialize_order(order_id=constants.ORDER_ID)
    assert order_obj.info == order_mock.info
    asset_obj = up42.initialize_asset(asset_id=constants.ASSET_ID)
    assert asset_obj.info == asset_mock.info


@pytest.fixture(autouse=True)
def setup_workspace(requests_mock):
    requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
    requests_mock.get(
        url="https://api.up42.com/users/me",
        json={"data": {"id": constants.WORKSPACE_ID}},
    )


def test_should_initialize_workflow(requests_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
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
        project_api_key=constants.PROJECT_APIKEY,
    )
    workflow_obj = up42.initialize_workflow(constants.WORKFLOW_ID)
    assert workflow_obj.info == workflow_mock.info
    assert workflow_obj.project_id == constants.PROJECT_ID


def test_should_initialize_jobtask(requests_mock):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
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
        project_api_key=constants.PROJECT_APIKEY,
    )
    jobtask_obj = up42.initialize_jobtask(constants.JOBTASK_ID, constants.JOB_ID)
    assert jobtask_obj.info == jobtask_mock.info
    assert jobtask_obj.project_id == constants.PROJECT_ID


def test_should_initialize_tasking():
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
    )
    result = up42.initialize_tasking()
    assert isinstance(result, tasking.Tasking)
