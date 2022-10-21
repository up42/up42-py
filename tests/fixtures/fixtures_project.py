import pytest
import requests_mock

from .fixtures_globals import (
    WORKSPACE_ID,
    PROJECT_NAME,
    PROJECT_DESCRIPTION,
    WORKFLOW_ID,
    WORKFLOW_NAME,
    WORKFLOW_DESCRIPTION,
    JOB_ID,
)

from ..context import (
    Project,
)


@pytest.fixture()
def project_mock(auth_mock, requests_mock):
    # info
    url_project_info = f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}"
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

    project = Project(auth=auth_mock, project_id=auth_mock.project_id)

    # create_workflow.
    url_create_workflow = (
        f"{project.auth._endpoint()}/projects/{project.project_id}/workflows/"
    )
    json_create_workflow = {
        "error": {},
        "data": {"id": WORKFLOW_ID, "displayId": "workflow_displayId_123"},
    }
    requests_mock.post(url=url_create_workflow, json=json_create_workflow)

    # workflow.info (for create_workflow)
    url_workflow_info = (
        f"{project.auth._endpoint()}/projects/"
        f"{project.project_id}/workflows/{WORKFLOW_ID}"
    )
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "description": WORKFLOW_DESCRIPTION,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

    # get_workflows
    url_get_workflows = (
        f"{project.auth._endpoint()}/projects/" f"{project.project_id}/workflows"
    )
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
    url_get_jobs_page_0 = (
        f"{project.auth._endpoint()}/projects/{project.project_id}/jobs?page=0"
    )
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
    url_get_jobs_page_1 = (
        f"{project.auth._endpoint()}/projects/{project.project_id}/jobs?page=1"
    )
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
    url_get_jobs_page_2 = (
        f"{project.auth._endpoint()}/projects/{project.project_id}/jobs?page=2"
    )
    json_get_jobs_page_2 = {"data": []}
    requests_mock.get(url=url_get_jobs_page_2, json=json_get_jobs_page_2)

    # project_settings
    url_project_settings = (
        f"{project.auth._endpoint()}/projects/{project.project_id}/settings"
    )
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
    url_projects_settings_update = (
        f"{project.auth._endpoint()}/projects/project_id_123/settings"
    )
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
def project_live(auth_live):
    project = Project(auth=auth_live, project_id=auth_live.project_id)
    return project


@pytest.fixture()
def project_mock_max_concurrent_jobs(project_mock):
    def _project_mock_max_concurrent_jobs(maximum=5):
        m = requests_mock.Mocker()
        url_project_info = (
            f"{project_mock.auth._endpoint()}/projects/{project_mock.project_id}"
        )
        m.get(url=url_project_info, json={"data": {"xyz": 789}, "error": {}})
        url_project_settings = (
            f"{project_mock.auth._endpoint()}/projects"
            f"/{project_mock.project_id}/settings"
        )
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
