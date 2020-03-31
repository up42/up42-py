from pathlib import Path
import tempfile
import requests_mock
import pytest

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    job_mock,
    job_live,
)
import up42  # pylint: disable=wrong-import-order


def test_job_get_info(job_mock):
    del job_mock.info

    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}"
        )
        m.get(url=url_job_info, text='{"data": {"xyz":789}, "error":{}}')

        info = job_mock._get_info()
    assert isinstance(job_mock, up42.Job)
    assert info["xyz"] == 789
    assert job_mock.info["xyz"] == 789

# pylint: disable=unused-argument
def test_get_status(job_mock):
    pass


def test_track_status(job_mock):
    pass


def test_cancel_job(job_mock):
    pass


def test_download_quicklook(job_mock):
    pass


def test_get_result_json(job_mock):
    pass


def test_get_log(job_mock):
    pass


def test_get_jobtasks(job_mock):
    pass


def test_get_jobtasks_result_json(job_mock):
    pass


def test_map_result(job_mock):
    pass


def test_job_download_result(job_mock):
    with requests_mock.Mocker() as m:
        download_url = "http://up42.api.com/abcdef"
        url_download_result = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}/downloads/results/"
        )
        m.get(url_download_result, json={"data": {"url": download_url}, "error": {}})

        out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
        out_tgz_file = open(out_tgz, "rb")
        m.get(url=download_url, content=out_tgz_file.read())

        with tempfile.TemporaryDirectory() as tempdir:
            out_files = job_mock.download_result(tempdir)
            for file in out_files:
                assert Path(file).exists()
            assert len(out_files) == 1


@pytest.mark.live
def test_job_download_result_live(job_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = job_live.download_result(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 1


@pytest.mark.live
def test_job_download_result_no_tiff_live(auth_live):
    with tempfile.TemporaryDirectory() as tempdir:
        job = up42.Job(
            auth=auth_live,
            project_id=auth_live.project_id,
            job_id="99bc9fab-cffa-4010-bdac-2b0620c7e1cb",
        )
        out_files = job.download_result(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 98
