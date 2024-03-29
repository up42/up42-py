import pytest

from up42.job import Job

from .fixtures_globals import (
    API_HOST,
    DOWNLOAD_URL,
    JOB_ID,
    JOB_ID_2,
    JOB_NAME,
    JOBTASK_ID,
    MOCK_CREDITS,
    PROJECT_ID,
    WORKFLOW_NAME,
)


@pytest.fixture()
def job_mock(auth_mock, requests_mock):
    url_job_info = f"{API_HOST}/projects/{PROJECT_ID}/jobs/{JOB_ID}"
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

    job = Job(auth=auth_mock, project_id=PROJECT_ID, job_id=JOB_ID)

    # get_jobtasks
    url_job_tasks = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/tasks/"
    requests_mock.get(url=url_job_tasks, json={"data": [{"id": JOBTASK_ID}]})

    # get_logs
    url_logs = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/tasks/{JOBTASK_ID}/logs"
    requests_mock.get(url_logs, json="")

    # quicklooks
    url_quicklook = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/tasks/{JOBTASK_ID}/outputs/quicklooks/"
    requests_mock.get(url_quicklook, json={"data": ["a_quicklook.png"]})

    # get_results_json
    url = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/outputs/data-json/"
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_jobtasks_results_json
    url = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/tasks/{JOBTASK_ID}/outputs/data-json"
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_download_url
    url_download_result = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/downloads/results/"
    requests_mock.get(url_download_result, json={"data": {"url": DOWNLOAD_URL}, "error": {}})

    # get_job_credits
    url_download_result = f"{API_HOST}/projects/{job.project_id}/jobs/{job.job_id}/credits"
    requests_mock.get(
        url_download_result,
        json=MOCK_CREDITS,
    )

    return job


@pytest.fixture()
def jobs_mock(auth_mock, requests_mock):
    url_job_info = f"{API_HOST}/projects/{PROJECT_ID}/jobs/{JOB_ID}"
    requests_mock.get(
        url=url_job_info,
        json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
    )

    job1 = Job(auth=auth_mock, project_id=PROJECT_ID, job_id=JOB_ID)

    url_job_info = f"{API_HOST}/projects/{PROJECT_ID}/jobs/{JOB_ID_2}"
    requests_mock.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

    job2 = Job(auth=auth_mock, project_id=PROJECT_ID, job_id=JOB_ID_2)
    return [job1, job2]
