from pathlib import Path
import tempfile
import geojson

import pytest

from .context import Job

# pylint: disable=unused-import,wrong-import-order
from .fixtures import (
    auth_mock,
    job_mock,
    jobs_mock,
    jobcollection_single_mock,
    jobcollection_multiple_mock,
    jobcollection_empty_mock,
    auth_live,
    jobs_live,
    jobcollection_live,
)
from .fixtures import (
    JOB_ID,
    JOB_ID_2,
)


def test_jobcollection(jobcollection_single_mock):
    assert len(jobcollection_single_mock.jobs) == 1


def test_jobcollection_multiple(jobcollection_multiple_mock):
    assert len(jobcollection_multiple_mock.jobs) == 2


def test_job_iterator(
    jobcollection_multiple_mock, jobcollection_empty_mock, requests_mock
):
    worker = lambda job: 1
    res = jobcollection_multiple_mock.apply(worker, only_succeeded=False)
    assert len(res) == 2
    assert res[JOB_ID] == 1
    assert res[JOB_ID_2] == 1

    worker = lambda job, add: add
    res = jobcollection_multiple_mock.apply(worker, add=5, only_succeeded=False)
    assert len(res) == 2
    assert res[JOB_ID] == 5
    assert res[JOB_ID_2] == 5

    status = ["FAILED", "SUCCEEDED"]
    for i, job in enumerate(jobcollection_multiple_mock):
        url_job_info = (
            f"{jobcollection_multiple_mock.auth._endpoint()}/projects/"
            f"{jobcollection_multiple_mock.project_id}/jobs/{job.job_id}"
        )
        requests_mock.get(
            url=url_job_info, json={"data": {"status": status[i]}, "error": {}}
        )

    res = jobcollection_multiple_mock.apply(worker, add=5, only_succeeded=True)
    assert len(res) == 1
    assert res["jobid_456"] == 5

    with pytest.raises(ValueError) as e:
        jobcollection_empty_mock.apply(worker, add=5, only_succeeded=True)
        assert (
            str(e)
            == "This is an empty JobCollection. Cannot apply over an empty job list."
        )


def test_jobcollection_info(jobcollection_single_mock, requests_mock):
    url_job_info = (
        f"{jobcollection_single_mock.auth._endpoint()}/projects/"
        f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

    info = jobcollection_single_mock.info
    assert isinstance(info, dict)
    assert info[jobcollection_single_mock[0].job_id] == {"xyz": 789}


@pytest.mark.parametrize("status", ["NOT STARTED", "PENDING", "RUNNING"])
def test_jobcollection_get_jobs_status(
    jobcollection_single_mock, status, requests_mock
):
    url_job_info = (
        f"{jobcollection_single_mock.auth._endpoint()}/projects/"
        f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"status": status}, "error": {}})

    job_statuses = jobcollection_single_mock.status
    assert isinstance(job_statuses, dict)
    assert job_statuses[jobcollection_single_mock[0].job_id] == status


def test_jobcollection_download_results(jobcollection_single_mock, requests_mock):
    download_url = "http://up42.api.com/abcdef"
    url_download_result = (
        f"{jobcollection_single_mock.auth._endpoint()}/projects/"
        f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}/downloads/results/"
    )
    requests_mock.get(
        url_download_result, json={"data": {"url": download_url}, "error": {}}
    )

    url_job_info = (
        f"{jobcollection_single_mock.auth._endpoint()}/projects/"
        f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(
        url=url_job_info, json={"data": {"status": "SUCCEEDED"}, "error": {}}
    )

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


def test_jobcollection_download_results_failed(
    jobcollection_single_mock, requests_mock
):
    url_job_info = (
        f"{jobcollection_single_mock.auth._endpoint()}/projects/"
        f"{jobcollection_single_mock.project_id}/jobs/{jobcollection_single_mock[0].job_id}"
    )
    requests_mock.get(
        url=url_job_info, json={"data": {"status": "FAILED"}, "error": {}}
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError) as e:
            jobcollection_single_mock.download_results(tmpdir, merge=False)
            assert (
                str(e)
                == "All jobs have failed! Cannot apply over an empty succeeded job list."
            )


def test_jobcollection_download_results_merged(
    jobcollection_multiple_mock, requests_mock
):
    download_url = "http://up42.api.com/abcdef"

    for job in jobcollection_multiple_mock.jobs:
        url_download_result = (
            f"{jobcollection_multiple_mock.auth._endpoint()}/projects/"
            f"{jobcollection_multiple_mock.project_id}/jobs/{job.job_id}/downloads/results/"
        )
        requests_mock.get(
            url_download_result, json={"data": {"url": download_url}, "error": {}}
        )

        url_job_info = (
            f"{jobcollection_multiple_mock.auth._endpoint()}/projects/"
            f"{jobcollection_multiple_mock.project_id}/jobs/{job.job_id}"
        )
        requests_mock.get(
            url=url_job_info, json={"data": {"status": "SUCCEEDED"}, "error": {}}
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
            assert (
                tmpdir / Path(merged_data_json.features[0].properties["up42.data_path"])
            ).exists()


def test_jobcollection_subscripted(jobcollection_single_mock):
    assert isinstance(jobcollection_single_mock[0], Job)
    assert jobcollection_single_mock[0].job_id == JOB_ID


def test_jobcollection_iterator(jobcollection_multiple_mock):
    for job in jobcollection_multiple_mock:
        assert isinstance(job, Job)


@pytest.mark.live
def test_jobcollection_download_results_live(jobcollection_live):
    with tempfile.TemporaryDirectory() as tmpdir:
        out_files_dict = jobcollection_live.download_results(Path(tmpdir), merge=False)
        jobid_1, jobid_2 = jobcollection_live.jobs_id
        for _, value in out_files_dict.items():
            for p in value:
                assert Path(p).exists()
        assert jobid_1 in out_files_dict
        assert jobid_2 in out_files_dict
        assert len(out_files_dict[jobid_1]) == 2
        assert len(out_files_dict[jobid_2]) == 2
