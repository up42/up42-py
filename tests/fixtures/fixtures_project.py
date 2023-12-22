import pytest
import requests_mock

from ..context import Project
from .fixtures_globals import (
    API_HOST,
    JOB_ID,
    PROJECT_DESCRIPTION,
    PROJECT_ID,
    PROJECT_NAME,
    WORKFLOW_DESCRIPTION,
    WORKFLOW_ID,
    WORKFLOW_NAME,
    WORKSPACE_ID,
)


@pytest.fixture()
def project_mock(auth_mock, requests_mock):
    # info
    url_project_info = f"{API_HOST}/projects/{PROJECT_ID}"
    json_project_info = {
        "data": {
            "xyz": 789,
            "workspaceId": WORKSPACE_ID,
            "name": PROJECT_NAME,
            "description": PROJECT_DESCRIPTION,
            "createdAt": "some_date",
        },
        "error": {},
    }
    requests_mock.get(url=url_project_info, json=json_project_info)

    project = Project(auth=auth_mock, project_id=PROJECT_ID)

    # create_workflow.
    url_create_workflow = f"{API_HOST}/projects/{PROJECT_ID}/workflows/"
    json_create_workflow = {
        "error": {},
        "data": {"id": WORKFLOW_ID, "displayId": "workflow_displayId_123"},
    }
    requests_mock.post(url=url_create_workflow, json=json_create_workflow)

    # workflow.info (for create_workflow)
    url_workflow_info = f"{API_HOST}/projects/" f"{project.project_id}/workflows/{WORKFLOW_ID}"
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "description": WORKFLOW_DESCRIPTION,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

    # get_workflows
    url_get_workflows = f"{API_HOST}/projects/" f"{PROJECT_ID}/workflows"
    json_get_workflows = {
        "data": [
            {
                "id": WORKFLOW_ID,
                "name": WORKFLOW_NAME,
                "description": WORKFLOW_DESCRIPTION,
            },
            {
                "id": WORKFLOW_ID,
                "name": WORKFLOW_NAME,
                "description": WORKFLOW_DESCRIPTION,
            },
        ],
        "error": {},
    }  # Same workflow_id to not have to get multiple .info
    requests_mock.get(url=url_get_workflows, json=json_get_workflows)

    # get_jobs_pagination.
    # page 0
    url_get_jobs_page_0 = f"{API_HOST}/projects/{PROJECT_ID}/jobs?page=0"
    json_get_jobs_page_0 = {
        "data": [
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
            }
        ]
        * 100
    }
    requests_mock.get(url=url_get_jobs_page_0, json=json_get_jobs_page_0)
    # page 1
    url_get_jobs_page_1 = f"{API_HOST}/projects/{PROJECT_ID}/jobs?page=1"
    json_get_jobs_page_1 = {
        "data": [
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
            }
        ]
        * 20
    }
    requests_mock.get(url=url_get_jobs_page_1, json=json_get_jobs_page_1)
    # page 2
    url_get_jobs_page_2 = f"{API_HOST}/projects/{PROJECT_ID}/jobs?page=2"
    json_get_jobs_page_2 = {"data": []}
    requests_mock.get(url=url_get_jobs_page_2, json=json_get_jobs_page_2)

    # project_settings
    url_project_settings = f"{API_HOST}/projects/{PROJECT_ID}/settings"
    json_project_settings = {
        "data": [
            {"name": "MAX_CONCURRENT_JOBS", "value": "10"},
            {"name": "MAX_AOI_SIZE", "value": "5000"},
            {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE", "value": "20"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_project_settings, json=json_project_settings)

    # project settings update
    url_projects_settings_update = f"{API_HOST}/projects/{PROJECT_ID}/settings"
    json_desired_project_settings = {
        "data": [
            {"name": "MAX_CONCURRENT_JOBS", "value": "500"},
            {"name": "MAX_AOI_SIZE", "value": "5"},
            {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE", "value": "20"},
        ],
        "error": {},
    }
    requests_mock.post(
        url_projects_settings_update,
        [
            {"status_code": 404, "json": json_desired_project_settings},
            {"status_code": 201, "json": json_desired_project_settings},
        ],
    )

    return project


@pytest.fixture()
def project_live(auth_live, project_id_live):
    project = Project(auth=auth_live, project_id=project_id_live)
    return project


@pytest.fixture()
def project_mock_max_concurrent_jobs(project_mock):
    def _project_mock_max_concurrent_jobs(maximum=5):
        m = requests_mock.Mocker()
        url_project_info = f"{API_HOST}/projects/{PROJECT_ID}"
        m.get(url=url_project_info, json={"data": {"xyz": 789}, "error": {}})
        url_project_settings = f"{API_HOST}/projects" f"/{PROJECT_ID}/settings"
        m.get(
            url=url_project_settings,
            json={
                "data": [
                    {"name": "MAX_CONCURRENT_JOBS", "value": str(maximum)},
                    {"name": "MAX_AOI_SIZE", "value": "1000"},
                    {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE", "value": "200"},
                ],
                "error": {},
            },
        )
        return m

    return _project_mock_max_concurrent_jobs
