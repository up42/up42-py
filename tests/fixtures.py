import os

import pytest
import requests_mock

from .context import Api, Catalog, Project, Workflow, Job, JobTask


@pytest.fixture()
def api_mock():
    api = Api(
        project_id="project_id123",
        project_api_key="project_apikey123",
        authenticate=False,
        retry=False,
    )
    api.token = "token_123"
    return api


@pytest.fixture()
def project_mock(api_mock):
    project = Project(api=api_mock, project_id=api_mock.project_id)
    return project


@pytest.fixture()
def workflow_mock(api_mock):
    workflow = Workflow(
        api=api_mock, workflow_id="workflow_id123", project_id=api_mock.project_id
    )
    return workflow


@pytest.fixture()
def job_mock(api_mock):
    pass


@pytest.fixture()
def jobtask_mock(api_mock):
    pass


################################################################


@pytest.fixture()
def project_mock_with_info(api_mock):
    api_mock.authenticate = True
    with requests_mock.Mocker() as m:
        url_project_info = f"{api_mock._endpoint()}/projects/{api_mock.project_id}"
        m.get(url=url_project_info, text='{"data": {"xyz":789}, "error":{}}')

        project = Project(api=api_mock, project_id=api_mock.project_id)
    return project


@pytest.fixture()
def workflow_mock_with_info(api_mock):
    api_mock.authenticate = True
    with requests_mock.Mocker() as m:
        url_workflow_info = (
            f"{workflow_mock.api._endpoint()}/projects/"
            f"{workflow_mock.project_id}/workflows/"
            f"{workflow_mock.workflow_id}"
        )
        m.get(url=url_workflow_info, text='{"data": {"xyz":789}, "error":{}}')

        workflow = Workflow(
            api=api_mock, workflow_id="workflow_id123", project_id=api_mock.project_id
        )
    return workflow


@pytest.fixture()
def job_mock_with_info(api_mock):
    pass


@pytest.fixture()
def jobtask_mock_with_info(api_mock):
    pass


################################################################


@pytest.fixture()
def api_live():
    api = Api(
        project_id=os.getenv("UP42_PROJECT_ID_test_up42_py"),
        project_api_key=os.getenv("UP42_PROJECT_API_KEY_test_up42_py"),
    )
    return api


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
