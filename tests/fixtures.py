import os

import pytest
import requests_mock

from .context import Auth, Project, Workflow, Job, Tools


@pytest.fixture()
def auth_mock():
    auth = Auth(
        project_id="project_id123",
        project_api_key="project_apikey123",
        authenticate=False,
        retry=False,
    )
    auth.token = "token_123"
    return auth


@pytest.fixture()
def project_mock(auth_mock):
    project = Project(auth=auth_mock, project_id=auth_mock.project_id)
    return project


@pytest.fixture()
def workflow_mock(auth_mock):
    workflow = Workflow(
        auth=auth_mock, workflow_id="workflow_id123", project_id=auth_mock.project_id
    )
    return workflow


@pytest.fixture()
def job_mock(auth_mock):
    job = Job(
        auth=auth_mock, project_id=auth_mock.project_id, job_id="job_id123"
    )
    return job


@pytest.fixture()
def jobtask_mock(auth_mock):
    pass


################################################################


@pytest.fixture()
def project_mock_with_info(auth_mock):
    auth_mock.authenticate = True
    with requests_mock.Mocker() as m:
        url_project_info = f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}"
        m.get(url=url_project_info, text='{"data": {"xyz":789}, "error":{}}')

        project = Project(auth=auth_mock, project_id=auth_mock.project_id)
    return project


@pytest.fixture()
def workflow_mock_with_info(auth_mock):
    auth_mock.authenticate = True
    with requests_mock.Mocker() as m:
        url_workflow_info = (
            f"{workflow_mock.auth._endpoint()}/projects/"
            f"{workflow_mock.project_id}/workflows/"
            f"{workflow_mock.workflow_id}"
        )
        m.get(url=url_workflow_info, text='{"data": {"xyz":789}, "error":{}}')

        workflow = Workflow(
            auth=auth_mock,
            workflow_id="workflow_id123",
            project_id=auth_mock.project_id,
        )
    return workflow


@pytest.fixture()
def job_mock_with_info(auth_mock):
    pass


@pytest.fixture()
def jobtask_mock_with_info(auth_mock):
    pass


################################################################


@pytest.fixture()
def auth_live():
    auth = Auth(
        project_id=os.getenv("UP42_PROJECT_ID_test_up42_py"),
        project_api_key=os.getenv("UP42_PROJECT_API_KEY_test_up42_py"),
    )
    return auth


@pytest.fixture()
def tools_live():
    auth_live = Auth(
        project_id=os.getenv("UP42_PROJECT_ID_test_up42_py"),
        project_api_key=os.getenv("UP42_PROJECT_API_KEY_test_up42_py"),
    )
    tools = Tools(auth=auth_live)
    return tools


@pytest.fixture()
def project_live():
    pass


@pytest.fixture()
def workflow_live():
    pass


@pytest.fixture()
def job_live():
    pass


@pytest.fixture()
def jobtask_live():
    pass
