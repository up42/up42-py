import os

import pytest

from .fixtures_globals import (
    WORKFLOW_NAME,
    JOB_ID,
    JOB_NAME,
    JOBTASK_ID,
    DOWNLOAD_URL,
    MOCK_CREDITS,
    JOB_ID_2,
)

from ..context import (
    Job,
)


@pytest.fixture()
def job_mock(auth_mock, requests_mock):
    url_job_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID}"
    )
    json_job_info = {
        "data": {
            "xyz": 789,
            "mode": "DEFAULT",
            "description": "some_description",
            "startedAt": "some_date",
            "workflowName": WORKFLOW_NAME,
            "name": JOB_NAME,
            "finishedAt": "some_date",
            "status": "SUCCESSFULL",
            "inputs": "some_inputs",
        },
        "error": {},
    }
    requests_mock.get(url=url_job_info, json=json_job_info)

    job = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=JOB_ID)

    # get_jobtasks
    url_job_tasks = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}/tasks/"
    )
    requests_mock.get(url=url_job_tasks, json={"data": [{"id": JOBTASK_ID}]})

    # get_logs
    url_logs = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/"
        f"{job.job_id}/tasks/{JOBTASK_ID}/logs"
    )
    requests_mock.get(url_logs, json="")

    # quicklooks
    url_quicklook = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}"
        f"/tasks/{JOBTASK_ID}/outputs/quicklooks/"
    )
    requests_mock.get(url_quicklook, json={"data": ["a_quicklook.png"]})

    # get_results_json
    url = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}"
        f"/outputs/data-json/"
    )
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_jobtasks_results_json
    url = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}"
        f"/tasks/{JOBTASK_ID}/outputs/data-json"
    )
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_download_url
    url_download_result = (
        f"{job.auth._endpoint()}/projects/"
        f"{job.project_id}/jobs/{job.job_id}/downloads/results/"
    )
    requests_mock.get(
        url_download_result, json={"data": {"url": DOWNLOAD_URL}, "error": {}}
    )

    # get_job_credits
    url_download_result = (
        f"{job.auth._endpoint()}/projects/"
        f"{job.project_id}/jobs/{job.job_id}/credits"
    )
    requests_mock.get(
        url_download_result,
        json=MOCK_CREDITS,
    )

    return job


@pytest.fixture()
def job_live(auth_live):
    job = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
    )
    return job


@pytest.fixture()
def jobs_mock(auth_mock, requests_mock):
    url_job_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID}"
    )
    requests_mock.get(
        url=url_job_info,
        json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
    )

    job1 = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=JOB_ID)

    url_job_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID_2}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

    job2 = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=JOB_ID_2)
    return [job1, job2]


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
