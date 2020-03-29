import os

import pytest
import requests_mock

from .fixtures import auth_mock, job_mock
import up42


def test_job_get_info(job_mock):
    del job_mock.info

    with requests_mock.Mocker() as m:
        url_job_info = f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
        m.get(url=url_job_info, text='{"data": {"xyz":789}, "error":{}}')

        info = job_mock._get_info()
    assert isinstance(job_mock, up42.Job)
    assert info["xyz"] == 789
    assert job_mock.info["xyz"] == 789
