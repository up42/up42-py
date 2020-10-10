import os

import pytest
import requests_mock

from .context import (
    Auth,
    Project,
    Workflow,
    Job,
    JobCollection,
    JobTask,
    Tools,
    Catalog,
)

# TODO: Use patch.dict instead of 2 fictures?
@pytest.fixture()
def auth_mock_no_request(requests_mock):
    auth = Auth(
        project_id="project_id123",
        project_api_key="project_apikey123",
        authenticate=False,
        retry=False,
        get_info=False,
    )

    url_get_token = (
        f"https://{auth.project_id}:"
        f"{auth.project_api_key}@api.up42."
        f"{auth.env}/oauth/token"
    )
    json_get_token = {"data": {"accessToken": "token_789"}}
    requests_mock.post(
        url=url_get_token,
        json=json_get_token,
    )

    return auth


@pytest.fixture()
def auth_mock(requests_mock):
    # token for initial authentication
    url_get_token = "https://project_id123:project_apikey123@api.up42.com/oauth/token"
    json_get_token = {"data": {"accessToken": "token_789"}}
    requests_mock.post(
        url=url_get_token,
        json=json_get_token,
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
        project_id=os.getenv("TEST_UP42_PROJECT_ID"),
        project_api_key=os.getenv("TEST_UP42_PROJECT_API_KEY"),
    )
    return auth


@pytest.fixture()
def project_mock(auth_mock, requests_mock):
    # info
    url_project_info = f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}"
    json_project_info = {"data": {"xyz": 789}, "error": {}}
    requests_mock.get(url=url_project_info, json=json_project_info)

    project = Project(auth=auth_mock, project_id=auth_mock.project_id)

    # create_workflow. If with use_existing=True, requires workflow info mock.
    url_create_workflow = (
        f"{project.auth._endpoint()}/projects/" f"{project.project_id}/workflows/"
    )
    json_create_workflow = {
        "error": {},
        "data": {"id": "workflow_id123", "displayId": "workflow_displayId123"},
    }
    requests_mock.post(url=url_create_workflow, json=json_create_workflow)

    # get_workflows
    url_get_workflows = (
        f"{auth_mock._endpoint()}/projects/" f"{project.project_id}/workflows"
    )
    json_get_workflows = {
        "data": [{"id": "workflow_id123"}, {"id": "workflow_id123"}],
        "error": {},
    }  # Same workflow_id to not have to get multiple .info
    requests_mock.get(url=url_get_workflows, json=json_get_workflows)

    # get_jobs. Requires job_info mock.
    job_id = "job_id123"
    url_get_jobs = f"{auth_mock._endpoint()}/projects/{project.project_id}/jobs"
    json_get_jobs = {
        "data": [
            {
                "id": job_id,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
            }
        ]
    }
    requests_mock.get(url=url_get_jobs, json=json_get_jobs)

    # project_settings
    url_project_settings = (
        f"{auth_mock._endpoint()}/projects/{project.project_id}/settings"
    )
    json_project_settings = {
        "data": [
            {"name": "MAX_CONCURRENT_JOBS"},
            {"name": "MAX_AOI_SIZE"},
            {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_project_settings, json=json_project_settings)

    return project


@pytest.fixture()
def project_live(auth_live):
    project = Project(auth=auth_live, project_id=auth_live.project_id)
    return project


@pytest.fixture()
def workflow_mock(auth_mock):
    workflow_id = "workflow_id123"
    with requests_mock.Mocker() as m:
        url_workflow_info = (
            f"{auth_mock._endpoint()}/projects/"
            f"{auth_mock.project_id}/workflows/"
            f"{workflow_id}"
        )
        m.get(
            url=url_workflow_info,
            json={"data": {"xyz": 789, "name": "workflow_name_123"}, "error": {}},
        )

        workflow = Workflow(
            auth=auth_mock,
            workflow_id=workflow_id,
            project_id=auth_mock.project_id,
        )
    return workflow


@pytest.fixture()
def workflow_live(auth_live):
    workflow = Workflow(
        auth=auth_live,
        project_id=auth_live.project_id,
        workflow_id=os.getenv("TEST_UP42_WORKFLOW_ID"),
    )
    return workflow


@pytest.fixture()
def job_mock(auth_mock):
    job_id = "jobid_123"

    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{job_id}"
        )
        m.get(
            url=url_job_info,
            json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
        )

        job = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=job_id)
    return job


@pytest.fixture()
def jobs_mock(auth_mock):
    with requests_mock.Mocker() as m:
        job_id = "jobid_123"
        url_job_info = (
            f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{job_id}"
        )
        m.get(
            url=url_job_info,
            json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
        )

        job1 = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=job_id)

        job_id = "jobid_456"
        url_job_info = (
            f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{job_id}"
        )
        m.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

        job2 = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=job_id)
    return [job1, job2]


@pytest.fixture()
def jobcollection_single_mock(auth_mock, job_mock):
    return JobCollection(
        auth=auth_mock, project_id=auth_mock.project_id, jobs=[job_mock]
    )


@pytest.fixture()
def jobcollection_multiple_mock(auth_mock, jobs_mock):
    return JobCollection(
        auth=auth_mock, project_id=auth_mock.project_id, jobs=jobs_mock
    )


@pytest.fixture()
def jobcollection_empty_mock(auth_mock):
    return JobCollection(auth=auth_mock, project_id=auth_mock.project_id, jobs=[])


@pytest.fixture()
def jobcollection_live(auth_live, jobs_live):
    return JobCollection(
        auth=auth_live, project_id=auth_live.project_id, jobs=jobs_live
    )


@pytest.fixture()
def job_live(auth_live):
    job = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
    )
    return job


@pytest.fixture()
def jobs_live(auth_live):
    job_1 = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
    )

    job_2 = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID_2"),
    )

    return [job_1, job_2]


@pytest.fixture()
def jobtask_mock(auth_mock):
    jobtask_id = "jobtaskid_123"
    job_id = "jobid_123"

    with requests_mock.Mocker() as m:
        url_jobtask_info = (
            f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{job_id}"
            f"/tasks/"
        )
        m.get(url=url_jobtask_info, json={"data": {"xyz": 789}, "error": {}})

        jobtask = JobTask(
            auth=auth_mock,
            project_id=auth_mock.project_id,
            job_id=job_id,
            jobtask_id=jobtask_id,
        )
    return jobtask


@pytest.fixture()
def jobtask_live(auth_live):
    jobtask = JobTask(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
        jobtask_id=os.getenv("TEST_UP42_JOBTASK_ID"),
    )
    return jobtask


@pytest.fixture()
def tools_mock(auth_mock):
    return Tools(auth=auth_mock)


@pytest.fixture()
def tools_live(auth_live):
    return Tools(auth=auth_live)


@pytest.fixture()
def catalog_mock(auth_mock):
    return Catalog(auth=auth_mock)


@pytest.fixture()
def catalog_live(auth_live):
    return Catalog(auth=auth_live)


@pytest.fixture()
def project_max_concurrent_jobs(project_mock):
    def _project_max_concurrent_jobs(maximum=5):
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

    return _project_max_concurrent_jobs
