import tempfile
from pathlib import Path

import pystac
import pytest

# pylint: disable=unused-import
from .context import Asset
from .fixtures import (
    ASSET_ID,
    DOWNLOAD_URL,
    DOWNLOAD_URL2,
    JSON_ASSET,
    STAC_ASSET_HREF,
    asset_live,
    asset_mock,
    asset_mock2,
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


def test_asset_stac_info(asset_mock):
    results_stac_asset = asset_mock.stac_info
    assert results_stac_asset
    assert results_stac_asset.extra_fields["up42-system:asset_id"] == ASSET_ID
    pystac_items = asset_mock.stac_items
    assert isinstance(pystac_items, pystac.ItemCollection)


def test_asset_update_metadata(asset_mock):
    updated_info = asset_mock.update_metadata(
        title="some_other_title", tags=["othertag1", "othertag2"]
    )
    assert updated_info["title"] == "some_other_title"
    assert updated_info["tags"] == ["othertag1", "othertag2"]


@pytest.mark.parametrize(
    "asset_fixture, download_url",
    [
        ("asset_mock", DOWNLOAD_URL),
        ("asset_mock2", DOWNLOAD_URL2),
    ],
)
def test_asset_get_download_url(asset_fixture, download_url, request):
    asset_fixture = request.getfixturevalue(asset_fixture)
    url = asset_fixture._get_download_url()
    assert url == download_url


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


@pytest.mark.parametrize(
    "asset_fixture, download_url, out_file_name",
    [
        ("asset_mock", DOWNLOAD_URL, "output.tgz"),
        (
            "asset_mock2",
            DOWNLOAD_URL2,
            "DS_SPOT6_202206240959075_FR1_FR1_SV1_SV1_E013N52_01709.tgz",
        ),
    ],
)
def test_asset_download_no_unpacking(
    asset_fixture, download_url, out_file_name, requests_mock, request
):
    asset_fixture = request.getfixturevalue(asset_fixture)
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=download_url,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    with tempfile.TemporaryDirectory() as tempdir:
        out_files = asset_fixture.download(tempdir, unpacking=False)
        for file in out_files:
            assert Path(file).exists()
            assert Path(file).name == out_file_name
        assert len(out_files) == 1


def test_download_stac_asset(asset_mock2, requests_mock):
    out_file_path = Path(__file__).resolve().parent / "mock_data/multipolygon.geojson"
    with open(out_file_path, "rb") as src_file:
        out_file = src_file.read()
    requests_mock.get(
        url=STAC_ASSET_HREF,
        content=out_file,
        headers={
            "Authorization": "Bearer some_token_value",
        },
    )
    with tempfile.TemporaryDirectory() as tempdir:
        out_path = asset_mock2.download_stac_asset(
            pystac.Asset(href=STAC_ASSET_HREF, roles=["data"]), tempdir
        )
        assert out_path.exists()
        assert out_path.name == "bsg-104-20230522-044750-90756881_ortho.tiff"
