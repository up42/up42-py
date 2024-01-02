from pathlib import Path
from unittest.mock import MagicMock

import pystac
import pytest

from up42.host import endpoint

# pylint: disable=unused-import
from .context import Asset
from .fixtures import (
    ASSET_ID,
    DOWNLOAD_URL,
    JSON_ASSET,
    STAC_ASSET_HREF,
    asset_mock,
    asset_mock2,
    assets_fixture,
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    storage_live,
    storage_mock,
    username_test_live,
)


@pytest.fixture
def auth_fixture(auth_mock):
    return {"auth_mock": auth_mock, "magic_mock": MagicMock()}


def test_init(asset_mock):
    assert isinstance(asset_mock, Asset)
    assert asset_mock.asset_id == ASSET_ID


def test_should_delegate_repr_to_info():
    asset_info = {"id": ASSET_ID, "other": "data"}
    asset = Asset(auth=MagicMock(), asset_info=asset_info)
    assert repr(asset) == repr(asset_info)


@pytest.mark.parametrize(
    "asset_id, asset_info, expected_error",
    [
        (
            None,
            None,
            "Either asset_id or asset_info should be provided in the constructor.",
        ),
        (
            "some_asset_id",
            {"id": ASSET_ID},
            "asset_id and asset_info cannot be provided simultaneously.",
        ),
    ],
    ids=[
        "Sc 1: Both asset_id and asset_info provided",
        "Sc 2: Both asset_id and asset_info not provided",
    ],
)
def test_init_should_accept_only_asset_id_or_info(asset_id, asset_info, expected_error):
    with pytest.raises(ValueError) as err:
        Asset(auth=MagicMock(), asset_id=asset_id, asset_info=asset_info)
    assert expected_error == str(err.value)


def test_should_initialize_with_retrieved_info(requests_mock, auth_mock):
    url_asset_info = endpoint(f"/v2/assets/{ASSET_ID}/metadata")
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)
    asset = Asset(auth=auth_mock, asset_id=ASSET_ID)
    assert asset.asset_id == ASSET_ID


def test_should_initialize_with_provided_info():
    provided_info = {"id": ASSET_ID, "name": "test name"}
    asset = Asset(auth=MagicMock(), asset_info=provided_info)
    assert asset.asset_id == ASSET_ID
    assert repr(asset.info) == repr(provided_info)


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


def test_asset_get_download_url(assets_fixture):
    asset_fixture = assets_fixture["asset_fixture"]
    download_url = assets_fixture["download_url"]
    url = asset_fixture._get_download_url()
    assert url == download_url


@pytest.mark.parametrize("with_output_directory", [True, False])
def test_asset_download(asset_mock, requests_mock, tmp_path, with_output_directory):
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    output_directory = tmp_path if with_output_directory else None
    out_files = asset_mock.download(output_directory)
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


def test_asset_download_no_unpacking(assets_fixture, requests_mock, tmp_path):
    asset_fixture = assets_fixture["asset_fixture"]
    download_url = assets_fixture["download_url"]
    out_file_name = assets_fixture["outfile_name"]
    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=download_url,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    out_files = asset_fixture.download(tmp_path, unpacking=False)
    for file in out_files:
        assert Path(file).exists()
        assert Path(file).name == out_file_name
    assert len(out_files) == 1


@pytest.mark.parametrize("with_output_directory", [True, False])
def test_download_stac_asset(
    asset_mock2, requests_mock, tmp_path, with_output_directory
):
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

    output_directory = tmp_path if with_output_directory else None
    out_path = asset_mock2.download_stac_asset(
        pystac.Asset(href=STAC_ASSET_HREF, roles=["data"]), output_directory
    )
    assert out_path.exists()
    assert out_path.name == "bsg-104-20230522-044750-90756881_ortho.tiff"
