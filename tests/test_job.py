import os
from pathlib import Path
import tempfile
import tarfile
from shutil import copyfile

import requests_mock
import pytest
from folium import Map

# pylint: disable=unused-import
from .context import Job, JobTask
from .fixtures import auth_mock, auth_live, job_mock, job_live, jobtask_mock


def test_job_get_info(job_mock):
    del job_mock.info

    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}"
        )
        m.get(url=url_job_info, text='{"data": {"xyz":789}, "error":{}}')

        info = job_mock._get_info()
    assert isinstance(job_mock, Job)
    assert info["xyz"] == 789
    assert job_mock.info["xyz"] == 789


# pylint: disable=unused-argument
@pytest.mark.parametrize("status", ["NOT STARTED", "PENDING", "RUNNING"])
def test_get_status(job_mock, status):
    del job_mock.info

    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}"
        )
        m.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

        job_status = job_mock.get_status()
    assert job_status == status


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
def test_is_succeeded(job_mock, status, expected):
    del job_mock.info

    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}"
        )
        m.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

        job_is_succeeded = job_mock.is_succeeded
    assert job_is_succeeded == expected


@pytest.mark.parametrize("status", ["SUCCEEDED"])
def test_track_status_pass(job_mock, status):
    del job_mock.info
    with requests_mock.Mocker() as m:
        url_job_info = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}"
        )
        m.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

        job_status = job_mock.track_status()
    assert job_status == status


@pytest.mark.parametrize("status", ["FAILED", "ERROR", "CANCELLED", "CANCELLING"])
def test_track_status_fail(job_mock, jobtask_mock, status):
    with pytest.raises(ValueError):
        del job_mock.info
        with requests_mock.Mocker() as m:
            url_job_info = (
                f"{job_mock.auth._endpoint()}/projects/"
                f"{job_mock.project_id}/jobs/{job_mock.job_id}"
            )
            m.get(url=url_job_info, json={"data": {"status": status}, "error": {}})
            url_job_tasks = (
                f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
                f"/tasks/"
            )
            m.get(url=url_job_tasks, json={"data": [{"id": jobtask_mock.jobtask_id}]})
            url_log = (
                f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/"
                f"{job_mock.job_id}/tasks/{jobtask_mock.jobtask_id}/logs"
            )
            m.get(url_log, json="")
            job_mock.track_status()


def test_cancel_job(job_mock):
    with requests_mock.Mocker() as m:
        url = f"{job_mock.auth._endpoint()}/jobs/{job_mock.job_id}/cancel/"
        m.post(url, status_code=200)
        job_mock.cancel_job()


def test_download_quicklook(job_mock, jobtask_mock):
    with tempfile.TemporaryDirectory() as tempdir:
        with requests_mock.Mocker() as m:
            url_job_tasks = (
                f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
                f"/tasks/"
            )
            m.get(url=url_job_tasks, json={"data": [{"id": jobtask_mock.jobtask_id}]})

            url_quicklook = (
                f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
                f"/tasks/{jobtask_mock.jobtask_id}/outputs/quicklooks/"
            )
            m.get(url_quicklook, json={"data": ["a_quicklook.png"]})
            url = (
                f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
                f"/tasks/{jobtask_mock.jobtask_id}/outputs/quicklooks/a_quicklook.png"
            )
            quicklook_file = (
                Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
            )

            m.get(url, content=open(quicklook_file, "rb").read())

            quick = job_mock.download_quicklooks(tempdir)
            assert len(quick) == 1
            assert Path(quick[0]).exists()
            assert Path(quick[0]).suffix == ".png"


def test_get_result_json(job_mock):
    with requests_mock.Mocker() as m:
        url = (
            f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
            f"/outputs/data-json/"
        )
        m.get(url, json={"type": "FeatureCollection", "features": []})
        assert job_mock.get_results_json() == {
            "type": "FeatureCollection",
            "features": [],
        }


def test_get_logs(job_mock, jobtask_mock):
    with requests_mock.Mocker() as m:
        url_job_tasks = (
            f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
            f"/tasks/"
        )
        m.get(url=url_job_tasks, json={"data": [{"id": jobtask_mock.jobtask_id}]})
        url_log = (
            f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/"
            f"{job_mock.job_id}/tasks/{jobtask_mock.jobtask_id}/logs"
        )
        m.get(url_log, json="")
        assert job_mock.get_logs(as_return=True)[jobtask_mock.jobtask_id] == ""
        assert not job_mock.get_logs()


def test_get_jobtasks(job_mock, jobtask_mock):
    with requests_mock.Mocker() as m:
        url_job_tasks = (
            f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
            f"/tasks/"
        )
        m.get(url=url_job_tasks, json={"data": [{"id": jobtask_mock.jobtask_id}]})
        job_tasks = job_mock.get_jobtasks()
        assert isinstance(job_tasks[0], JobTask)
        assert job_tasks[0].jobtask_id == jobtask_mock.jobtask_id


def test_get_jobtasks_result_json(job_mock, jobtask_mock):
    with requests_mock.Mocker() as m:
        url_job_tasks = (
            f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
            f"/tasks/"
        )
        m.get(url=url_job_tasks, json={"data": [{"id": jobtask_mock.jobtask_id}]})
        url = (
            f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/jobs/{job_mock.job_id}"
            f"/tasks/{jobtask_mock.jobtask_id}/outputs/data-json"
        )
        m.get(url, json={"type": "FeatureCollection", "features": [],})
        res = job_mock.get_jobtasks_results_json()
        assert len(res) == 1
        assert res[jobtask_mock.jobtask_id] == {
            "type": "FeatureCollection",
            "features": [],
        }


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
        m.get(
            url=download_url,
            content=out_tgz_file.read(),
            headers={"x-goog-stored-content-length": "163"},
        )

        with tempfile.TemporaryDirectory() as tempdir:
            out_files = job_mock.download_results(tempdir)
            out_paths = [Path(p) for p in out_files]
            for path in out_paths:
                assert path.exists()
            assert len(out_paths) == 2
            assert out_paths[0].name == "data.json"
            assert out_paths[1].parent.exists()
            assert out_paths[1].parent.is_dir()


def test_job_download_result_nounpacking(job_mock):
    with requests_mock.Mocker() as m:
        download_url = "http://up42.api.com/abcdef"
        url_download_result = (
            f"{job_mock.auth._endpoint()}/projects/"
            f"{job_mock.project_id}/jobs/{job_mock.job_id}/downloads/results/"
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
            out_files = job_mock.download_results(tempdir, unpacking=False)
            for file in out_files:
                assert Path(file).exists()
            assert len(out_files) == 1


@pytest.mark.live
def test_job_download_result_live(job_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = job_live.download_results(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 2


@pytest.mark.live
def test_job_download_result_no_tiff_live(auth_live):
    with tempfile.TemporaryDirectory() as tempdir:
        job = Job(
            auth=auth_live,
            project_id=auth_live.project_id,
            job_id=os.getenv("TEST_UP42_JOB_ID_NC_FILE"),
        )
        out_files = job.download_results(Path(tempdir))
        assert Path(out_files[0]).exists()
        assert Path(out_files[1]).exists()
        assert any(".nc" in s for s in out_files)
        assert any("data.json" in s for s in out_files)
        assert len(out_files) == 2


@pytest.mark.live
def test_job_download_result_dimap_live(auth_live):
    with tempfile.TemporaryDirectory() as tempdir:
        job = Job(
            auth=auth_live,
            project_id=auth_live.project_id,
            job_id=os.getenv("TEST_UP42_JOB_ID_DIMAP_FILE"),
        )
        out_files = job.download_results(Path(tempdir))
        print(out_files)
        assert Path(out_files[0]).exists()
        assert Path(out_files[20]).exists()
        assert Path(out_files[1]).exists()
        assert Path(out_files[1]).name == "data.json"
        assert len(out_files) == 44


@pytest.mark.skip
@pytest.mark.live
def test_job_download_result_live_2gb_big_exceeding_2min_gcs_treshold(auth_live):
    job = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id="30f82b44-1505-4773-ab23-31fa61ba9b4c",
    )
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = job.download_results(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 490


def test_map_results(job_mock):
    fp_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with tarfile.open(fp_tgz) as tar:
        tar.extractall(fp_tgz.parent)
    fp_tif = (
        fp_tgz.parent
        / "output/7e17f023-a8e3-43bd-aaac-5bbef749c7f4/7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif"
    )
    fp_data_json = fp_tgz.parent / "output/data.json"

    job_mock.results = [str(fp_tif), str(fp_data_json)]
    map_object = job_mock.map_results()
    assert isinstance(map_object, Map)


def test_map_results_additional_geojson(job_mock):
    fp_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with tarfile.open(fp_tgz) as tar:
        tar.extractall(fp_tgz.parent)
    fp_tif = (
        fp_tgz.parent
        / "output/7e17f023-a8e3-43bd-aaac-5bbef749c7f4/7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif"
    )
    fp_data_json = fp_tgz.parent / "output/data.json"
    fp_data_geojson = fp_tgz.parent / "output/additional_vector_file.geojson"
    copyfile(fp_data_json, fp_data_geojson)

    job_mock.results = [str(fp_tif), str(fp_data_json), str(fp_data_geojson)]
    map_object = job_mock.map_results()
    assert isinstance(map_object, Map)
