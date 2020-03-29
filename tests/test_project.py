import requests_mock

from .context import Project, Workflow
from .fixtures import auth_mock, project_mock


def test_project_get_info(project_mock):
    del project_mock.info

    with requests_mock.Mocker() as m:
        url_project_info = (
            f"{project_mock.auth._endpoint()}/projects/{project_mock.project_id}"
        )
        m.get(url=url_project_info, text='{"data": {"xyz":789}, "error":{}}')

        info = project_mock._get_info()
    assert isinstance(project_mock, Project)
    assert info["xyz"] == 789
    assert project_mock.info["xyz"] == 789


def test_get_workflows():
    pass


def test_create_workflow(project_mock):
    project_mock.auth.get_info = False

    with requests_mock.Mocker() as m:
        url_workflow_creation = f"{project_mock.auth._endpoint()}/projects/{project_mock.project_id}/workflows/"
        text_workflow_creation = '{"error":null,"data":{"id":"workflow_id123","displayId":"workflow_displayId123"}}'
        m.post(
            url=url_workflow_creation, text=text_workflow_creation,
        )

        workflow = project_mock.create_workflow(
            name="workflow_name123", description="workflow_description123"
        )
    assert isinstance(workflow, Workflow)
    assert not hasattr(workflow, "info")


def test_create_workflow_use_existing(project_mock):
    pass
