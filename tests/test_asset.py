import datetime
import json
import pathlib
from typing import Dict, List, Optional
from unittest import mock

import pystac
import pytest
import requests_mock as req_mock

from up42 import asset
from up42 import auth as up42_auth
from up42 import host

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


class TestStacMetadata:
    def test_should_get_stac_items_with_retries(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(
            constants.URL_STAC_SEARCH,
            [{"status_code": 401}, {"json": constants.STAC_SEARCH_RESPONSE}],
        )
        asset_obj = asset.Asset(auth_mock, asset_info={"id": constants.ASSET_ID})
        expected = pystac.ItemCollection.from_dict(constants.STAC_SEARCH_RESPONSE)
        assert asset_obj.stac_items.to_dict() == expected.to_dict()

    def test_fails_to_get_stac_items_after_retries(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(constants.URL_STAC_SEARCH, status_code=401)
        asset_obj = asset.Asset(auth_mock, asset_info={"id": constants.ASSET_ID})
        with pytest.raises(ValueError):
            _ = asset_obj.stac_items

    def test_should_get_stac_info_with_retries(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(
            constants.URL_STAC_SEARCH,
            [{"status_code": 401}, {"json": constants.STAC_SEARCH_RESPONSE}],
        )
        expected = pystac.Collection(
            id="up42-storage",
            description="UP42 Storage STAC API",
            extra_fields={"up42-system:asset_id": constants.ASSET_ID},
            extent=pystac.Extent(
                spatial=pystac.SpatialExtent(bboxes=[[1.0, 2.0, 3.0, 4.0]]),
                temporal=pystac.TemporalExtent(intervals=[[datetime.datetime.now(), None]]),
            ),
        )
        expected.add_link(
            pystac.Link(
                target=constants.URL_STAC_CATALOG,
                rel="root",
                title="UP42 Storage",
                media_type=pystac.MediaType.JSON,
            )
        )
        requests_mock.get(
            url=f"{constants.API_HOST}/v2/assets/stac/collections/{constants.STAC_COLLECTION_ID}",
            json=expected.to_dict(),
        )
        asset_obj = asset.Asset(auth_mock, asset_info={"id": constants.ASSET_ID})
        assert asset_obj.stac_info.to_dict() == expected.to_dict()

    def test_fails_to_get_stac_info_if_items_are_empty(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(
            constants.URL_STAC_SEARCH,
            json={"type": "FeatureCollection", "features": []},
        )
        asset_obj = asset.Asset(auth_mock, asset_info={"id": constants.ASSET_ID})
        with pytest.raises(ValueError):
            _ = asset_obj.stac_info

    def test_fails_to_get_stac_info_after_retries(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(constants.URL_STAC_SEARCH, status_code=401)
        asset_obj = asset.Asset(auth_mock, asset_info={"id": constants.ASSET_ID})
        with pytest.raises(Exception):
            _ = asset_obj.stac_info


def match_request_body(data: Dict):
    def matcher(request):
        return request.text == json.dumps(data)

    return matcher


class TestAssetUpdateMetadata:
    asset_info = {"id": constants.ASSET_ID, "title": "title", "tags": ["tag1"]}
    endpoint_url = f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID}/metadata"

    @pytest.mark.parametrize("title", [None, "new-title"])
    @pytest.mark.parametrize("tags", [None, [], ["tag1", "tag2"]])
    def test_should_update_metadata(
        self,
        auth_mock: up42_auth.Auth,
        requests_mock: req_mock.Mocker,
        title: Optional[str],
        tags: Optional[List[str]],
    ):
        asset_obj = asset.Asset(auth_mock, asset_info=self.asset_info)
        update_payload = {"title": title, "tags": tags}
        expected_info = {**self.asset_info, **update_payload}
        requests_mock.post(
            url=self.endpoint_url,
            json=expected_info,
            additional_matcher=match_request_body(update_payload),
        )
        assert asset_obj.update_metadata(title=title, tags=tags) == expected_info

    def test_should_not_update_title_if_not_provided(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        asset_obj = asset.Asset(auth_mock, asset_info=self.asset_info)
        tags = ["tag1", "tag2"]
        update_payload = {"tags": tags}
        expected_info = {**self.asset_info, **update_payload}
        requests_mock.post(
            url=self.endpoint_url,
            json=expected_info,
            additional_matcher=match_request_body(update_payload),
        )
        assert asset_obj.update_metadata(tags=tags) == expected_info

    def test_should_not_update_tags_if_not_provided(self, auth_mock: up42_auth.Auth, requests_mock: req_mock.Mocker):
        asset_obj = asset.Asset(auth_mock, asset_info=self.asset_info)
        title = "new-title"
        update_payload = {"title": title}
        expected_info = {**self.asset_info, **update_payload}
        requests_mock.post(
            url=self.endpoint_url,
            json=expected_info,
            additional_matcher=match_request_body(update_payload),
        )
        assert asset_obj.update_metadata(title=title) == expected_info


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
