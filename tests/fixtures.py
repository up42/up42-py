import os

import pytest
import requests_mock

from .context import Auth, Project, Workflow, Job, JobTask, Tools


@pytest.fixture()
def auth_mock_no_request():
    auth = Auth(
        project_id="project_id123",
        project_api_key="project_apikey123",
        authenticate=False,
        retry=False,
        get_info=False,
    )
    return auth


@pytest.fixture()
def auth_mock():
    with requests_mock.Mocker() as m:
        url_token = f"https://project_id123:project_apikey123@api.up42.com/oauth/token"
        m.post(
            url=url_token, text='{"data":{"accessToken":"token_789"}}',
        )
        auth = Auth(
            project_id="project_id123",
            project_api_key="project_apikey123",
            authenticate=True,
            retry=False,
            get_info=True,
        )
    return auth


@pytest.fixture()
def auth_live():
    auth = Auth(
        project_id=os.getenv("UP42_PROJECT_ID_test_up42_py"),
        project_api_key=os.getenv("UP42_PROJECT_API_KEY_test_up42_py"),
    )
    return auth


@pytest.fixture()
def project_mock(auth_mock):
    with requests_mock.Mocker() as m:
        url_project_info = f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}"
        m.get(url=url_project_info, text='{"data": {"xyz":789}, "error":{}}')

        project = Project(auth=auth_mock, project_id=auth_mock.project_id)
    return project


@pytest.fixture()
def project_live():
    pass


@pytest.fixture()
def workflow_mock(auth_mock):
    workflow_id = "workflow_id123"
    with requests_mock.Mocker() as m:
        url_workflow_info = (
            f"{auth_mock._endpoint()}/projects/"
            f"{auth_mock.project_id}/workflows/"
            f"{workflow_id}"
        )
        m.get(url=url_workflow_info, text='{"data": {"xyz":789}, "error":{}}')

        workflow = Workflow(
            auth=auth_mock, workflow_id=workflow_id, project_id=auth_mock.project_id,
        )
    return workflow


@pytest.fixture()
def workflow_live():
    pass


@pytest.fixture()
def job_mock(auth_mock):
    job_id = "jobid_123"
    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{job_id}"
        )
        m.get(url=url_job_info, text='{"data": {"xyz":789}, "error":{}}')

        job = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=job_id)
    return job


@pytest.fixture()
def job_live():
    pass


@pytest.fixture()
def jobtask_mock(auth_mock):
    pass


@pytest.fixture()
def jobtask_live():
    pass


@pytest.fixture()
def tools_live(auth_live):
    return Tools(auth=auth_live)
