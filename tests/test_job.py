import os
import tempfile
from pathlib import Path

import pytest

from up42.job import Job
from up42.jobtask import JobTask

from .fixtures.fixtures_globals import API_HOST, DOWNLOAD_URL, JOBTASK_ID


def test_job_info(job_mock):
    del job_mock._info
    assert isinstance(job_mock, Job)
    assert job_mock.info["xyz"] == 789
    assert job_mock._info["xyz"] == 789


@pytest.mark.parametrize("status", ["NOT STARTED", "PENDING", "RUNNING"])
def test_job_status(job_mock, status, requests_mock):
    del job_mock._info

    url_job_info = f"{API_HOST}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
    requests_mock.get(url=url_job_info, json={"data": {"status": status}, "error": {}})
    assert job_mock.status == status


# pylint: disable=unused-argument
@pytest.mark.parametrize(
    "status,expected",
    [
        ("NOT STARTED", False),
        ("PENDING", False),
        ("RUNNING", False),
        ("FAILED", False),
        ("SUCCEEDED", True),
    ],
)
def test_is_succeeded(job_mock, status, expected, requests_mock):
    del job_mock._info

    url_job_info = f"{API_HOST}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
    requests_mock.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

    assert job_mock.is_succeeded == expected


def test_download_quicklook(job_mock, requests_mock):
    url = (
        f"{API_HOST}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
        f"/tasks/{JOBTASK_ID}/outputs/quicklooks/a_quicklook.png"
    )
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(url, content=open(quicklook_file, "rb").read())

    with tempfile.TemporaryDirectory() as tempdir:
        quick = job_mock.download_quicklooks(tempdir)
        assert len(quick) == 1
        assert Path(quick[0]).exists()
        assert Path(quick[0]).suffix == ".png"


def test_get_result_json(job_mock):
    assert job_mock.get_results_json() == {
        "type": "FeatureCollection",
        "features": [],
    }


def test_get_logs(job_mock):
    assert job_mock.get_logs(as_return=True)[JOBTASK_ID] == ""
    assert not job_mock.get_logs()


def test_get_jobtasks(job_mock):
    job_tasks = job_mock.get_jobtasks()
    assert isinstance(job_tasks[0], JobTask)
    assert job_tasks[0].jobtask_id == JOBTASK_ID


def test_get_jobtasks_result_json(job_mock):
    res = job_mock.get_jobtasks_results_json()
    assert len(res) == 1
    assert res[JOBTASK_ID] == {
        "type": "FeatureCollection",
        "features": [],
    }


def test_job_download_result(job_mock, requests_mock):
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    with tempfile.TemporaryDirectory() as tempdir:
        out_files = job_mock.download_results(tempdir)
        out_paths = [Path(p) for p in out_files]
        for path in out_paths:
            assert path.exists()
        assert len(out_paths) == 2
        assert out_paths[0].name in [
            "7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif",
            "data.json",
        ]
        assert out_paths[1].name in [
            "7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif",
            "data.json",
        ]
        assert out_paths[0] != out_paths[1]
        assert out_paths[1].parent.exists()
        assert out_paths[1].parent.is_dir()


def test_job_download_gcs_no_unpacking(job_mock, requests_mock):
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    with tempfile.TemporaryDirectory() as tempdir:
        out_files = job_mock.download_results(tempdir, unpacking=False)
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 1


@pytest.mark.live
def test_job_download_result_dimap_live(auth_live, project_id_live):
    with tempfile.TemporaryDirectory() as tempdir:
        job = Job(
            auth=auth_live,
            project_id=project_id_live,
            job_id=os.getenv("TEST_UP42_JOB_ID_DIMAP_FILE"),
        )
        out_files = job.download_results(Path(tempdir))
        print(out_files)
        assert Path(out_files[0]).exists()
        assert Path(out_files[20]).exists()
        assert Path(out_files[-1]).exists()
        assert "data.json" in [Path(of).name for of in out_files]
        assert len(out_files) == 44


@pytest.mark.skip(reason="2gb download takes long")
@pytest.mark.live
def test_job_download_result_live_2gb_big_exceeding_2min_gcs_treshold(auth_live, project_id_live):
    job = Job(
        auth=auth_live,
        project_id=project_id_live,
        job_id="30f82b44-1505-4773-ab23-31fa61ba9b4c",
    )
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = job.download_results(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 490


def test_job_get_credits(job_mock):
    out_files = job_mock.get_credits()

    assert isinstance(out_files, dict)
    assert out_files == {"creditsUsed": 100}
