import os

import pytest

from .fixtures_globals import (
    PROJECT_DESCRIPTION,
    WORKFLOW_ID,
    WORKFLOW_NAME,
    JOB_ID,
    JSON_WORKFLOW_TASKS,
    JOB_NAME,
)

from ..context import (
    Workflow,
)


@pytest.fixture()
def workflow_mock_empty(auth_mock, requests_mock):
    """
    Only to test error handling of functions that don't correctly work on workflows
    without tasks (blocks). For the fully mocked workflow see workflow_mock fixture.
    """
    # info
    url_workflow_info = (
        f"{auth_mock._endpoint()}/projects/"
        f"{auth_mock.project_id}/workflows/"
        f"{WORKFLOW_ID}"
    )
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "id": WORKFLOW_ID,
            "description": PROJECT_DESCRIPTION,
            "createdAt": "some_date",
            "xyz": 789,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

    workflow = Workflow(
        auth=auth_mock,
        workflow_id=WORKFLOW_ID,
        project_id=auth_mock.project_id,
    )

    # get_workflow_tasks
    json_empty_workflow_tasks = {
        "error": "None",
        "data": [],
    }
    url_workflow_tasks = (
        f"{workflow.auth._endpoint()}/projects/{workflow.auth.project_id}/workflows/"
        f"{workflow.workflow_id}/tasks"
    )
    requests_mock.get(url=url_workflow_tasks, json=json_empty_workflow_tasks)

    return workflow


@pytest.fixture()
def workflow_mock(auth_mock, requests_mock):
    # info
    url_workflow_info = (
        f"{auth_mock._endpoint()}/projects/"
        f"{auth_mock.project_id}/workflows/"
        f"{WORKFLOW_ID}"
    )
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "id": WORKFLOW_ID,
            "description": PROJECT_DESCRIPTION,
            "createdAt": "some_date",
            "xyz": 789,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

    workflow = Workflow(
        auth=auth_mock,
        workflow_id=WORKFLOW_ID,
        project_id=auth_mock.project_id,
    )

    # get_workflow_tasks
    url_workflow_tasks = (
        f"{workflow.auth._endpoint()}/projects/{workflow.auth.project_id}/workflows/"
        f"{workflow.workflow_id}/tasks"
    )
    requests_mock.get(url=url_workflow_tasks, json=JSON_WORKFLOW_TASKS)

    # get_compatible_blocks
    url_compatible_blocks = (
        f"{workflow.auth._endpoint()}/projects/{workflow.project_id}/"
        f"workflows/{workflow.workflow_id}/compatible-blocks?parentTaskName=tiling:1"
    )
    json_compatible_blocks = {
        "data": {
            "blocks": [
                {"blockId": "aaa123", "name": "aaa", "versionTag": "2.0"},
                {"blockId": "bbb123", "name": "bbb", "versionTag": "2.0"},
            ],
            "error": {},
        }
    }
    requests_mock.get(url=url_compatible_blocks, json=json_compatible_blocks)

    # run_job
    url_run_job = (
        f"{workflow.auth._endpoint()}/projects/{workflow.project_id}/"
        f"workflows/{workflow.workflow_id}/jobs?name={JOB_NAME + '_py'}"
    )
    json_run_job = {"data": {"id": JOB_ID}}
    requests_mock.post(url=url_run_job, json=json_run_job)

    # get_jobs
    url_get_jobs = f"{workflow.auth._endpoint()}/projects/{workflow.project_id}/jobs"
    json_get_jobs = {
        "data": [
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
                "workflowId": "123456",
            },
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
                "workflowId": workflow.workflow_id,
            },
        ]
    }
    requests_mock.get(url=url_get_jobs, json=json_get_jobs)

    return workflow


@pytest.fixture()
def workflow_live(auth_live):
    workflow = Workflow(
        auth=auth_live,
        project_id=auth_live.project_id,
        workflow_id=os.getenv("TEST_UP42_WORKFLOW_ID"),
    )
    return workflow
