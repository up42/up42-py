import os

import pytest

from .fixtures_globals import JOB_ID, JOBTASK_ID, JOBTASK_NAME, DOWNLOAD_URL

from ..context import (
    JobTask,
)


@pytest.fixture()
def jobtask_mock(auth_mock, requests_mock):
    # info
    url_jobtask_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID}"
        f"/tasks/"
    )
    requests_mock.get(
        url=url_jobtask_info,
        json={
            "data": [
                {
                    "id": JOBTASK_ID,
                    "xyz": 789,
                    "name": JOBTASK_NAME,
                    "status": "SUCCESSFULL",
                    "startedAt": "some_date",
                    "finishedAt": "some_date",
                    "block": {"name": "a_block"},
                    "blockVersion": "1.0.0",
                }
            ],
            "error": {},
        },
    )

    jobtask = JobTask(
        auth=auth_mock,
        project_id=auth_mock.project_id,
        job_id=JOB_ID,
        jobtask_id=JOBTASK_ID,
    )

    # get_results_json
    url_results_json = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.auth.project_id}/"
        f"jobs/{jobtask.job_id}/tasks/{jobtask.jobtask_id}/"
        f"outputs/data-json/"
    )
    requests_mock.get(
        url_results_json, json={"type": "FeatureCollection", "features": []}
    )

    # get_download_url
    url_download_result = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.project_id}/"
        f"jobs/{jobtask.job_id}/tasks/{jobtask.jobtask_id}/"
        f"downloads/results/"
    )
    requests_mock.get(
        url_download_result, json={"data": {"url": DOWNLOAD_URL}, "error": {}}
    )

    # quicklooks
    url_quicklook = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.project_id}/"
        f"jobs/{jobtask.job_id}"
        f"/tasks/{jobtask.jobtask_id}/outputs/quicklooks/"
    )
    requests_mock.get(url_quicklook, json={"data": ["a_quicklook.png"]})

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
