import requests_mock
import pytest

from .context import Project, Workflow

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    project_mock,
    project_live,
)


def test_project_get_info(project_mock):
    del project_mock.info

    with requests_mock.Mocker() as m:
        url_project_info = (
            f"{project_mock.auth._endpoint()}/projects/{project_mock.project_id}"
        )
        m.get(url=url_project_info, json={"data": {"xyz": 789}, "error": {}})

        info = project_mock._get_info()
    assert isinstance(project_mock, Project)
    assert info["xyz"] == 789
    assert project_mock.info["xyz"] == 789


def test_create_workflow(project_mock):
    project_mock.auth.get_info = False

    with requests_mock.Mocker() as m:
        url_workflow_creation = (
            f"{project_mock.auth._endpoint()}/projects/"
            f"{project_mock.project_id}/workflows/"
        )
        json_workflow_creation = {
            "error": {},
            "data": {"id": "workflow_id123", "displayId": "workflow_displayId123"},
        }
        m.post(
            url=url_workflow_creation, json=json_workflow_creation,
        )

        workflow = project_mock.create_workflow(
            name="workflow_name123", description="workflow_description123"
        )
    assert isinstance(workflow, Workflow)
    assert not hasattr(workflow, "info")


def test_create_workflow_use_existing(project_mock):
    with requests_mock.Mocker() as m:
        url_workflows_get = (
            f"{project_mock.auth._endpoint()}/projects/"
            f"{project_mock.project_id}/workflows"
        )
        m.get(
            url=url_workflows_get,
            json={"data": [{"id": "workflow_id123"}], "error": {}},
        )

        url_workflow_info = (
            f"{project_mock.auth._endpoint()}/projects/"
            f"{project_mock.project_id}/workflows/workflow_id123"
        )
        m.get(
            url=url_workflow_info,
            json={
                "data": {
                    "name": "workflow_name123",
                    "description": "workflow_description123",
                },
                "error": {},
            },
        )

        workflow = project_mock.create_workflow(
            name="workflow_name123",
            description="workflow_description123",
            use_existing=True,
        )
    assert isinstance(workflow, Workflow)


def test_get_workflows(project_mock):
    project_mock.auth.get_info = False

    with requests_mock.Mocker() as m:
        url_workflows_get = (
            f"{project_mock.auth._endpoint()}/projects/"
            f"{project_mock.project_id}/workflows"
        )
        m.get(
            url=url_workflows_get,
            json={
                "data": [{"id": "workflow_id123"}, {"id": "workflow_id789"}],
                "error": {},
            },
        )

        workflows = project_mock.get_workflows()

    assert len(workflows) == 2
    assert isinstance(workflows[0], Workflow)


@pytest.mark.live
def test_get_workflows_live(project_live):
    workflows = project_live.get_workflows()
    assert isinstance(workflows[0], Workflow)
    assert workflows[0].project_id == project_live.project_id


def test_get_project_settings(project_mock):
    with requests_mock.Mocker() as m:
        url_project_settings = (
            f"{project_mock.auth._endpoint()}/projects"
            f"/{project_mock.project_id}/settings"
        )
        m.get(
            url=url_project_settings,
            json={
                "data": [
                    {"name": "MAX_CONCURRENT_JOBS"},
                    {"name": "MAX_AOI_SIZE"},
                    {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE"},
                ],
                "error": {},
            },
        )

        project_settings = project_mock.get_project_settings()
    assert isinstance(project_settings, list)
    assert len(project_settings) == 3
    assert project_settings[0]["name"] == "MAX_CONCURRENT_JOBS"


@pytest.mark.live
def test_get_project_settings_live(project_live):
    project_settings = project_live.get_project_settings()
    assert isinstance(project_settings, list)
    assert len(project_settings) == 3
    assert project_settings[0]["name"] == "MAX_CONCURRENT_JOBS"
