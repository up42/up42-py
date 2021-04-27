import os
from pathlib import Path
import tempfile
import pytest

# pylint: disable=unused-import
from .context import Asset
from .fixtures import (
    ASSET_ID,
    DOWNLOAD_URL,
    JSON_ASSET,
    auth_mock,
    auth_live,
    asset_mock,
    asset_live,
)


def test_init(asset_mock):
    assert isinstance(asset_mock, Asset)
    assert asset_mock.asset_id == ASSET_ID


def test_asset_info(asset_mock):
    assert asset_mock.info
    assert asset_mock.info["id"] == ASSET_ID
    assert asset_mock.info["name"] == JSON_ASSET["data"]["name"]


@pytest.mark.live
def test_asset_info_live(asset_live):
    assert asset_live.info
    assert asset_live.info["id"] == os.getenv("TEST_UP42_ASSET_ID")
    assert asset_live.info["name"]


def test_asset_source(asset_mock):
    assert asset_mock.source == "BLOCK"


@pytest.mark.live
def test_asset_source_live(asset_live):
    assert asset_live.source == "BLOCK"


def test_asset_get_download_url(asset_mock):
    url = asset_mock._get_download_url()
    assert url == DOWNLOAD_URL


@pytest.mark.live
def test_asset_get_download_url_live(asset_live):
    url = asset_live._get_download_url()
    assert url


def test_asset_download(asset_mock, requests_mock):
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    with tempfile.TemporaryDirectory() as tempdir:
        out_files = asset_mock.download(tempdir)
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


def test_asset_download_nounpacking(asset_mock, requests_mock):

    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    with tempfile.TemporaryDirectory() as tempdir:
        out_files = asset_mock.download(tempdir, unpacking=False)
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 1


@pytest.mark.live
def test_asset_download_live(asset_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = asset_live.download(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 54
