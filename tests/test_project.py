import pytest
from .context import Project, Workflow, Job

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    project_mock,
    project_live,
    project_mock_max_concurrent_jobs,
)
from .fixtures import (
    WORKFLOW_ID,
    WORKFLOW_NAME,
    WORKFLOW_DESCRIPTION,
    JOB_ID,
)


def test_project_info(project_mock):
    del project_mock._info

    assert isinstance(project_mock, Project)
    assert project_mock.info["xyz"] == 789
    assert project_mock._info["xyz"] == 789


def test_create_workflow(project_mock):
    project_mock.auth.get_info = False

    workflow = project_mock.create_workflow(
        name=WORKFLOW_NAME, description=WORKFLOW_DESCRIPTION
    )
    assert isinstance(workflow, Workflow)
    assert not hasattr(workflow, "_info")


def test_create_workflow_use_existing(project_mock, requests_mock):
    url_workflow_info = (
        f"{project_mock.auth._endpoint()}/projects/"
        f"{project_mock.project_id}/workflows/{WORKFLOW_ID}"
    )
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "description": WORKFLOW_DESCRIPTION,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

    workflow = project_mock.create_workflow(
        name=WORKFLOW_NAME,
        description=WORKFLOW_DESCRIPTION,
        use_existing=True,
    )
    assert isinstance(workflow, Workflow)


def test_get_workflows(project_mock):
    project_mock.auth.get_info = False

    workflows = project_mock.get_workflows()
    assert len(workflows) == 2
    assert isinstance(workflows[0], Workflow)


@pytest.mark.live
def test_get_workflows_live(project_live):
    workflows = project_live.get_workflows()
    assert isinstance(workflows[0], Workflow)
    assert workflows[0].project_id == project_live.project_id


def test_get_jobs(project_mock, requests_mock):
    url_job_info = (
        f"{project_mock.auth._endpoint()}/projects/"
        f"{project_mock.project_id}/jobs/{JOB_ID}"
    )
    json_job_info = {"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}}
    requests_mock.get(
        url=url_job_info,
        json=json_job_info,
    )

    jobcollection = project_mock.get_jobs()
    assert isinstance(jobcollection.jobs, list)
    assert isinstance(jobcollection.jobs[0], Job)
    assert jobcollection.jobs[0].job_id == JOB_ID


@pytest.mark.skip
@pytest.mark.live
def test_get_jobs_live(project_live):
    # Skip by default as too many jobs in test project, triggers too many job info
    # requests.
    jobcollection = project_live.get_jobs()
    assert isinstance(jobcollection.jobs, list)
    assert isinstance(jobcollection.jobs[0], Job)


def test_get_project_settings(project_mock):
    project_settings = project_mock.get_project_settings()
    assert isinstance(project_settings, list)
    assert len(project_settings) == 3
    assert project_settings[0]["name"] == "MAX_CONCURRENT_JOBS"


@pytest.mark.live
def test_get_project_settings_live(project_live):
    project_settings = project_live.get_project_settings()
    assert isinstance(project_settings, list)
    assert len(project_settings) == 3
    project_settings_dict = {item["name"]: item for item in project_settings}
    assert "MAX_CONCURRENT_JOBS" in project_settings_dict.keys()


def test_max_concurrent_jobs(project_mock, project_mock_max_concurrent_jobs):
    with project_mock_max_concurrent_jobs(5):
        max_concurrent_jobs = project_mock.max_concurrent_jobs
    assert max_concurrent_jobs == 5


@pytest.mark.live
def test_max_concurrent_jobs_live(project_live):
    max_concurrent_jobs = project_live.max_concurrent_jobs
    assert max_concurrent_jobs == 100
