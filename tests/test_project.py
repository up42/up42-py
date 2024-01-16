import pytest
import requests

from .context import Job, Project, Workflow

# pylint: disable=unused-import
from .fixtures import (
    JOB_ID,
    WORKFLOW_DESCRIPTION,
    WORKFLOW_NAME,
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    project_live,
    project_mock,
    project_mock_max_concurrent_jobs,
    username_test_live,
)
from .fixtures.fixtures_globals import API_HOST

MAX_CONCURRENT_JOBS = 12


def test_project_info(project_mock):
    del project_mock._info

    assert isinstance(project_mock, Project)
    assert project_mock.info["xyz"] == 789
    assert project_mock._info["xyz"] == 789


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
    url_job_info = f"{API_HOST}/projects/" f"{project_mock.project_id}/jobs/{JOB_ID}"
    json_job_info = {"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}}
    requests_mock.get(
        url=url_job_info,
        json=json_job_info,
    )

    jobcollection = project_mock.get_jobs()
    assert isinstance(jobcollection.jobs, list)
    assert isinstance(jobcollection.jobs[0], Job)
    assert jobcollection.jobs[0].job_id == JOB_ID


def test_get_jobs_pagination(project_mock):
    jobcollection = project_mock.get_jobs()
    assert isinstance(jobcollection.jobs, list)
    assert isinstance(jobcollection.jobs[0], Job)
    assert jobcollection.jobs[0].job_id == JOB_ID
    assert len(jobcollection.jobs) == 120


def test_get_jobs_pagination_limit(project_mock):
    jobcollection = project_mock.get_jobs(limit=110)
    assert len(jobcollection.jobs) == 110


@pytest.mark.skip(
    reason="too many jobs in test project, triggers too many job info requests."
)
@pytest.mark.live
def test_get_jobs_live(project_live):
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
    assert project_settings[0]["name"] in [
        "JOB_QUERY_MAX_AOI_SIZE",
        "MAX_CONCURRENT_JOBS",
        "'JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE'",
    ]
