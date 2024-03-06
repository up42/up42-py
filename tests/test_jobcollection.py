import tempfile
from pathlib import Path

import geojson
import pytest

from up42.job import Job

from .fixtures.fixtures_globals import API_HOST, JOB_ID, JOB_ID_2


def test_jobcollection(jobcollection_single_mock):
    assert len(jobcollection_single_mock.jobs) == 1


def test_jobcollection_multiple(jobcollection_multiple_mock):
    assert len(jobcollection_multiple_mock.jobs) == 2


def test_job_iterator(jobcollection_multiple_mock, jobcollection_empty_mock, requests_mock):
    def worker(job):
        return 1

    res = jobcollection_multiple_mock.apply(worker, only_succeeded=False)
    assert len(res) == 2
    assert res[JOB_ID] == 1
    assert res[JOB_ID_2] == 1

    def worker_with_add(job, add):
        return add

    res = jobcollection_multiple_mock.apply(worker_with_add, add=5, only_succeeded=False)
    assert len(res) == 2
    assert res[JOB_ID] == 5
    assert res[JOB_ID_2] == 5

    status = ["FAILED", "SUCCEEDED"]
    for i, job in enumerate(jobcollection_multiple_mock):
        url_job_info = f"{API_HOST}/projects/" f"{jobcollection_multiple_mock.project_id}/jobs/{job.job_id}"
        requests_mock.get(url=url_job_info, json={"data": {"status": status[i]}, "error": {}})

    res = jobcollection_multiple_mock.apply(worker_with_add, add=5, only_succeeded=True)
    assert len(res) == 1
    assert res[JOB_ID_2] == 5

    with pytest.raises(ValueError) as e:
        jobcollection_empty_mock.apply(worker_with_add, add=5, only_succeeded=True)
        assert str(e) == "This is an empty JobCollection. Cannot apply over an empty job list."


def test_jobcollection_info(jobcollection_single_mock, requests_mock):
    url_job_info = (
        f"{API_HOST}/projects/" f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

    info = jobcollection_single_mock.info
    assert isinstance(info, dict)
    assert info[jobcollection_single_mock[0].job_id] == {"xyz": 789}


@pytest.mark.parametrize("status", ["NOT STARTED", "PENDING", "RUNNING"])
def test_jobcollection_jobs_status(jobcollection_single_mock, status, requests_mock):
    url_job_info = (
        f"{API_HOST}/projects/" f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

    job_statuses = jobcollection_single_mock.status
    assert isinstance(job_statuses, dict)
    assert job_statuses[jobcollection_single_mock[0].job_id] == status


def test_jobcollection_download_results(jobcollection_single_mock, requests_mock):
    download_url = "http://up42.api.com/abcdef"
    url_download_result = (
        f"{API_HOST}/projects/"
        f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}/downloads/results/"
    )
    requests_mock.get(url_download_result, json={"data": {"url": download_url}, "error": {}})

    url_job_info = (
        f"{API_HOST}/projects/" f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"status": "SUCCEEDED"}, "error": {}})

    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as out_tgz_file:
        requests_mock.get(
            url=download_url,
            content=out_tgz_file.read(),
            headers={"x-goog-stored-content-length": "163"},
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dict = jobcollection_single_mock.download_results(tmpdir, merge=False)
        for job_id in out_dict:
            assert Path(out_dict[job_id][0]).exists()
            assert len(out_dict[job_id]) == 2


def test_jobcollection_download_results_failed(jobcollection_single_mock, requests_mock):
    url_job_info = (
        f"{API_HOST}/projects/" f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"status": "FAILED"}, "error": {}})
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError) as e:
            jobcollection_single_mock.download_results(tmpdir, merge=False)
            assert str(e) == "All jobs have failed! Cannot apply over an empty succeeded job list."


def test_jobcollection_download_results_merged(jobcollection_multiple_mock, requests_mock):
    download_url = "http://up42.api.com/abcdef"

    for job in jobcollection_multiple_mock.jobs:
        url_download_result = (
            f"{API_HOST}/projects/" f"{jobcollection_multiple_mock.project_id}/jobs/{job.job_id}/downloads/results/"
        )
        requests_mock.get(
            url_download_result,
            json={"data": {"url": download_url}, "error": {}},
        )

        url_job_info = f"{API_HOST}/projects/" f"{jobcollection_multiple_mock.project_id}/jobs/{job.job_id}"
        requests_mock.get(
            url=url_job_info,
            json={"data": {"status": "SUCCEEDED"}, "error": {}},
        )

    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as out_tgz_file:
        requests_mock.get(
            url=download_url,
            content=out_tgz_file.read(),
            headers={"x-goog-stored-content-length": "163"},
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dict = jobcollection_multiple_mock.download_results(tmpdir, merge=True)
        print(out_dict)
        assert len(out_dict) == 3
        assert Path(out_dict["merged_result"][0]).exists()
        assert len(out_dict["merged_result"]) == 1
        for job_id in out_dict:
            if job_id not in "merged_result":
                assert Path(out_dict[job_id][0]).exists()
                assert len(out_dict[job_id]) == 2

        with open(out_dict["merged_result"][0]) as src:
            merged_data_json = geojson.load(src)
            print(merged_data_json)
            assert len(merged_data_json.features) == 2
            assert merged_data_json.features[0].properties["job_id"] == JOB_ID
            assert JOB_ID in merged_data_json.features[0].properties["up42.data_path"]
            assert (tmpdir / Path(merged_data_json.features[0].properties["up42.data_path"])).exists()


def test_jobcollection_subscripted(jobcollection_single_mock):
    assert isinstance(jobcollection_single_mock[0], Job)
    assert jobcollection_single_mock[0].job_id == JOB_ID


def test_jobcollection_iterator(jobcollection_multiple_mock):
    for job in jobcollection_multiple_mock:
        assert isinstance(job, Job)
