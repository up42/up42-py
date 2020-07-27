from pathlib import Path
import tempfile

import pytest
import requests_mock

# pylint: disable=unused-import,wrong-import-order
from .fixtures import (
    auth_mock,
    job_mock,
    jobcollection_mock,
    auth_live,
    jobs_live,
    jobcollection_live,
)


def test_jobcollection(jobcollection_mock):
    assert len(jobcollection_mock.jobs) == 1


def test_jobcollection_download_result(jobcollection_mock):
    with requests_mock.Mocker() as m:
        download_url = "http://up42.api.com/abcdef"
        url_download_result = (
            f"{jobcollection_mock.auth._endpoint()}/projects/"
            f"{jobcollection_mock.project_id}/jobs/{jobcollection_mock.jobs_id[0]}/downloads/results/"
        )
        m.get(url_download_result, json={"data": {"url": download_url}, "error": {}})

        out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
        out_tgz_file = open(out_tgz, "rb")
        m.get(
            url=download_url,
            content=out_tgz_file.read(),
            headers={"x-goog-stored-content-length": "163"},
        )

        with tempfile.TemporaryDirectory() as tempdir:
            out_dict = jobcollection_mock.download_results(tempdir)
            for job_id in out_dict:
                assert Path(out_dict[job_id][0]).exists()
                assert len(out_dict[job_id]) == 2


@pytest.mark.live
def test_jobcollection_download_result_live(jobcollection_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files_dict = jobcollection_live.download_results(Path(tempdir))
        jobid_1, jobid_2 = jobcollection_live.jobs_id
        for _, value in out_files_dict.items():
            for p in value:
                assert Path(p).exists()
        assert jobid_1 in out_files_dict
        assert jobid_2 in out_files_dict
        assert len(out_files_dict[jobid_1]) == 2
        assert len(out_files_dict[jobid_2]) == 2
