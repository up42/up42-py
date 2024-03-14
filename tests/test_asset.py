import pathlib
from unittest import mock

import pystac
import pytest

from up42 import asset, host

from .fixtures import fixtures_globals as constants


def test_init(asset_mock):
    assert isinstance(asset_mock, asset.Asset)
    assert asset_mock.asset_id == constants.ASSET_ID


def test_should_delegate_repr_to_info():
    asset_info = {"id": constants.ASSET_ID, "other": "data"}
    asset_obj = asset.Asset(auth=mock.MagicMock(), asset_info=asset_info)
    assert repr(asset_obj) == repr(asset_info)


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
            {"id": constants.ASSET_ID},
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
        asset.Asset(auth=mock.MagicMock(), asset_id=asset_id, asset_info=asset_info)
    assert expected_error == str(err.value)


def test_should_initialize_with_retrieved_info(requests_mock, auth_mock):
    url_asset_info = host.endpoint(f"/v2/assets/{constants.ASSET_ID}/metadata")
    requests_mock.get(url=url_asset_info, json=constants.JSON_ASSET)
    asset_obj = asset.Asset(auth=auth_mock, asset_id=constants.ASSET_ID)
    assert asset_obj.info == constants.JSON_ASSET


def test_should_initialize_with_provided_info():
    provided_info = {"id": constants.ASSET_ID, "name": "test name"}
    asset_obj = asset.Asset(auth=mock.MagicMock(), asset_info=provided_info)
    assert asset_obj.asset_id == constants.ASSET_ID
    assert asset_obj.info == provided_info


def test_asset_info(asset_mock):
    assert asset_mock.info
    assert asset_mock.info["id"] == constants.ASSET_ID
    assert asset_mock.info["name"] == constants.JSON_ASSET["name"]


def test_asset_stac_info(asset_mock):
    results_stac_asset = asset_mock.stac_info
    assert results_stac_asset
    assert results_stac_asset.extra_fields["up42-system:asset_id"] == constants.ASSET_ID
    pystac_items = asset_mock.stac_items
    assert isinstance(pystac_items, pystac.ItemCollection)


def test_asset_update_metadata(asset_mock):
    updated_info = asset_mock.update_metadata(title="some_other_title", tags=["othertag1", "othertag2"])
    assert updated_info["title"] == "some_other_title"
    assert updated_info["tags"] == ["othertag1", "othertag2"]


@pytest.mark.parametrize("with_output_directory", [True, False])
def test_asset_download(asset_mock, requests_mock, tmp_path, with_output_directory):
    out_tgz = pathlib.Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=constants.DOWNLOAD_URL,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    output_directory = tmp_path if with_output_directory else None
    out_files = asset_mock.download(output_directory)
    out_paths = [pathlib.Path(p) for p in out_files]
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
    out_tgz = pathlib.Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=download_url,
        content=out_tgz_file,
        headers={"x-goog-stored-content-length": "163"},
    )

    out_files = asset_fixture.download(tmp_path, unpacking=False)
    for file in out_files:
        assert pathlib.Path(file).exists()
        assert pathlib.Path(file).name == out_file_name
    assert len(out_files) == 1


@pytest.mark.parametrize("with_output_directory", [True, False])
def test_download_stac_asset(asset_mock2, requests_mock, tmp_path, with_output_directory):
    out_file_path = pathlib.Path(__file__).resolve().parent / "mock_data/multipolygon.geojson"
    with open(out_file_path, "rb") as src_file:
        out_file = src_file.read()
    requests_mock.get(
        url=constants.STAC_ASSET_HREF,
        content=out_file,
        headers={
            "Authorization": "Bearer some_token_value",
        },
    )

    output_directory = tmp_path if with_output_directory else None
    out_path = asset_mock2.download_stac_asset(
        pystac.Asset(href=constants.STAC_ASSET_HREF, roles=["data"]), output_directory
    )
    assert out_path.exists()
    assert out_path.name == "bsg-104-20230522-044750-90756881_ortho.tiff"
