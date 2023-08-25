from pathlib import Path
import tempfile
import shutil


# pylint: disable=unused-import
from .context import JobTask
from .fixtures import auth_mock, auth_live, jobtask_mock
from .fixtures import DOWNLOAD_URL


def test_info(jobtask_mock):
    del jobtask_mock._info


def test_get_results_json(jobtask_mock):
    results_json = jobtask_mock.get_results_json()
    assert results_json == {
        "type": "FeatureCollection",
        "features": [],
    }


def test_jobtask_download_result(jobtask_mock, requests_mock):
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "221"},
    )

    # With specified outdir
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = jobtask_mock.download_results(output_directory=tempdir)
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 2

    # With default outdir
    default_outdir = (
        Path.cwd()
        / f"project_{jobtask_mock.auth.project_id}/job_{jobtask_mock.job_id}/jobtask_{jobtask_mock.jobtask_id}"
    )
    if default_outdir.exists():
        shutil.rmtree(default_outdir)
    out_files = jobtask_mock.download_results()
    assert default_outdir.exists()
    assert default_outdir.is_dir()
    for file in out_files:
        assert Path(file).exists()
    assert len(out_files) == 2
    assert str(default_outdir) in str(out_files[0])
    shutil.rmtree(default_outdir)


def test_download_quicklook(jobtask_mock, requests_mock):
    url_download_quicklooks = (
        f"{jobtask_mock.auth._endpoint()}/projects/{jobtask_mock.project_id}/"
        f"jobs/{jobtask_mock.job_id}"
        f"/tasks/{jobtask_mock.jobtask_id}/outputs/quicklooks/a_quicklook.png"
    )
    quicklook_file = Path(__file__).resolve().parent / "mock_data/a_quicklook.png"
    requests_mock.get(
        url_download_quicklooks, content=open(quicklook_file, "rb").read()
    )

    with tempfile.TemporaryDirectory() as tempdir:
        quick = jobtask_mock.download_quicklooks(tempdir)
        assert len(quick) == 1
        assert Path(quick[0]).exists()
        assert Path(quick[0]).suffix == ".png"
