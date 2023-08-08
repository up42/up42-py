import os
import tempfile
from pathlib import Path

import pystac
import pytest

# pylint: disable=unused-import
from .context import Asset
from .fixtures import (
    ASSET_ID,
    DOWNLOAD_URL,
    JSON_ASSET,
    asset_live,
    asset_mock,
    auth_live,
    auth_mock,
)


def test_init(asset_mock):
    assert isinstance(asset_mock, Asset)
    assert asset_mock.asset_id == ASSET_ID


def test_asset_info(asset_mock):
    assert asset_mock.info
    assert asset_mock.info["id"] == ASSET_ID
    assert asset_mock.info["name"] == JSON_ASSET["name"]


@pytest.mark.live
def test_asset_info_live(asset_live):
    assert asset_live.info
    assert asset_live.info["id"] == os.getenv("TEST_UP42_ASSET_ID")
    assert asset_live.info["name"]


def test_asset_stac_info(asset_mock):
    assert asset_mock.stac_info
    assert asset_mock.stac_info.extra_fields["up42-system:asset_id"] == os.getenv(
        "TEST_UP42_ASSET_ID"
    )
    pystac_items = asset_mock.stac_items
    assert isinstance(pystac_items, pystac.ItemCollection)


@pytest.mark.live
def test_asset_stac_info_live(asset_live):
    assert asset_live.stac_info
    assert asset_live.stac_info.extra_fields["up42-system:asset_id"] == os.getenv(
        "TEST_UP42_ASSET_ID"
    )
    pystac_items = asset_live.stac_items
    assert isinstance(pystac_items, pystac.ItemCollection)


def test_asset_update_metadata(asset_mock):
    updated_info = asset_mock.update_metadata(
        title="some_other_title", tags=["othertag1", "othertag2"]
    )
    assert updated_info["title"] == "some_other_title"
    assert updated_info["tags"] == ["othertag1", "othertag2"]


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


@pytest.mark.live
def test_asset_download_live(asset_live):
    """
    tgz from block (storage)
    """
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = asset_live.download(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 44


@pytest.mark.live
def test_asset_download_live_2(asset_live):
    """
    zip from order (storage)
    """
    asset_live.asset_id = os.getenv("TEST_UP42_ASSET_ID_2_zip")
    with tempfile.TemporaryDirectory() as tempdir:
        out_files = asset_live.download(Path(tempdir))
        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 42


def test_asset_download_no_unpacking(asset_mock, requests_mock):
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
            assert Path(file).name == "output.tgz"
        assert len(out_files) == 1
