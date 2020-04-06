from pathlib import Path
import tempfile

import requests_mock
import pytest

# pylint: disable=unused-import
from .fixtures import auth_mock, auth_live, jobtask_mock, jobtask_live
import up42  # pylint: disable=wrong-import-order


def test_get_info(jobtask_mock):
    del jobtask_mock.info

    with requests_mock.Mocker() as m:
        url_jobtask_info = (
            f"{jobtask_mock.auth._endpoint()}/"
            f"projects/{jobtask_mock.project_id}/jobs/"
            f"{jobtask_mock.job_id}/tasks/"
        )
        m.get(url=url_jobtask_info, text='{"data": {"xyz":789}, "error":{}}')

        info = jobtask_mock._get_info()
    assert isinstance(jobtask_mock, up42.JobTask)
    assert info["xyz"] == 789
    assert jobtask_mock.info["xyz"] == 789


def test_get_result_json(jobtask_mock):
    with requests_mock.Mocker() as m:
        url = (
            f"{jobtask_mock.auth._endpoint()}/projects/{jobtask_mock.auth.project_id}/"
            f"jobs/{jobtask_mock.job_id}/tasks/{jobtask_mock.jobtask_id}/"
            f"outputs/data-json/"
        )
        m.get(url, json={"type": "FeatureCollection", "features": []})
        assert jobtask_mock.get_results_json() == {
            "type": "FeatureCollection",
            "features": [],
        }


@pytest.mark.live
def test_get_result_json_live(jobtask_live):
    result_json = jobtask_live.get_results_json()
    assert result_json["type"] == "FeatureCollection"
    assert len(result_json["features"][0]["bbox"]) == 4


def test_jobtask_download_result(jobtask_mock):
    with requests_mock.Mocker() as m:
        download_url = "http://up42.api.com/abcdef"
        url_download_result = (
            f"{jobtask_mock.auth._endpoint()}/projects/{jobtask_mock.project_id}/"
            f"jobs/{jobtask_mock.job_id}/tasks/{jobtask_mock.jobtask_id}/"
            f"downloads/results/"
        )
        m.get(url_download_result, json={"data": {"url": download_url}, "error": {}})

        out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
        out_tgz_file = open(out_tgz, "rb")
        m.get(
            url=download_url,
            content=out_tgz_file.read(),
            headers={"x-goog-stored-content-length": "221"},
        )

        with tempfile.TemporaryDirectory() as tempdir:
            out_files = jobtask_mock.download_results(output_directory=tempdir)
            for file in out_files:
                assert Path(file).exists()
            assert len(out_files) == 1


@pytest.mark.live
def test_jobtask_download_result_live(jobtask_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = jobtask_live.download_results(output_directory=tempdir)
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 1
        assert Path(out_files[0]).suffix == ".tif"


def test_download_quicklook(jobtask_mock):
    with tempfile.TemporaryDirectory() as tempdir:
        with requests_mock.Mocker() as m:
            url_quicklook = (
                f"{jobtask_mock.auth._endpoint()}/projects/{jobtask_mock.project_id}/"
                f"jobs/{jobtask_mock.job_id}"
                f"/tasks/{jobtask_mock.jobtask_id}/outputs/quicklooks/"
            )
            m.get(url_quicklook, json={"data": ["a_quicklook.png"]})
            url = (
                f"{jobtask_mock.auth._endpoint()}/projects/{jobtask_mock.project_id}/"
                f"jobs/{jobtask_mock.job_id}"
                f"/tasks/{jobtask_mock.jobtask_id}/outputs/quicklooks/a_quicklook.png"
            )
            quicklook_file = (
                Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
            )

            m.get(url, content=open(quicklook_file, "rb").read())

            quick = jobtask_mock.download_quicklooks(tempdir)
            assert len(quick) == 1
            assert Path(quick[0]).exists()
            assert Path(quick[0]).suffix == ".png"


@pytest.mark.live
def test_download_quicklook_live(jobtask_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = jobtask_live.download_quicklooks(output_directory=tempdir)
        assert len(out_files) == 1
        assert Path(out_files[0]).exists()
        assert Path(out_files[0]).suffix == ".png"
