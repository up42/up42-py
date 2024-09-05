import datetime
import pathlib
from typing import List, Optional
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from up42 import asset, host

from . import helpers
from .fixtures import fixtures_globals as constants


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        workspace_mock.auth.session = requests.session()
        workspace_mock.id = constants.WORKSPACE_ID
        yield


class TestAsset:
    asset_info = {"id": constants.ASSET_ID, "other": "data"}

    @pytest.fixture(params=["output_dir", "no_output_dir"])
    def output_directory(self, request, tmp_path) -> Optional[str]:
        return tmp_path if request.param == "output_dir" else None

    @pytest.fixture(params=["unpack", "no_unpack"])
    def expected_files(self, requests_mock: req_mock.Mocker, request) -> List[str]:
        sample_tgz = pathlib.Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
        with open(sample_tgz, "rb") as src_tgz:
            sample_tgz_content = src_tgz.read()
            requests_mock.get(
                url=constants.DOWNLOAD_URL,
                content=sample_tgz_content,
                headers={"x-goog-stored-content-length": "163"},
            )
            sample_files = (
                [
                    "7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif",
                    "data.json",
                ]
                if request.param == "unpack"
                else ["output.tgz"]
            )
            return sample_files

    @pytest.fixture()
    def expected_stac_files(self, requests_mock: req_mock.Mocker) -> str:
        sample_stac = pathlib.Path(__file__).resolve().parent / "mock_data/multipolygon.geojson"
        with open(sample_stac, "rb") as src_file:
            out_file = src_file.read()
            requests_mock.get(
                url=constants.STAC_ASSET_URL,
                content=out_file,
            )
            return "bsg-104-20230522-044750-90756881_ortho.tiff"

    def test_should_delegate_repr_to_info(self):
        assert repr(asset.Asset(asset_info=self.asset_info)) == repr(self.asset_info)

    def test_should_initialize(self, requests_mock: req_mock.Mocker):
        url = host.endpoint(f"/v2/assets/{constants.ASSET_ID}/metadata")
        requests_mock.get(url=url, json=self.asset_info)
        assert asset.Asset(asset_id=constants.ASSET_ID).info == self.asset_info

    def test_should_initialize_with_info_provided(self):
        assert asset.Asset(asset_info=self.asset_info).info == self.asset_info

    @pytest.mark.parametrize(
        "asset_id, asset_info, expected_error",
        [
            (
                None,
                None,
                "Either asset_id or asset_info should be provided in the constructor.",
            ),
            (
                constants.ASSET_ID,
                {"id": constants.ASSET_ID},
                "asset_id and asset_info cannot be provided simultaneously.",
            ),
        ],
        ids=[
            "Both asset_id and asset_info provided",
            "Neither asset_id and asset_info provided",
        ],
    )
    def test_fails_initialize_with_concurrent_or_empty_info_id(
        self, asset_id: Optional[str], asset_info: Optional[dict], expected_error: str
    ):
        with pytest.raises(ValueError, match=expected_error):
            asset.Asset(asset_id=asset_id, asset_info=asset_info)

    def test_should_download_expected_files(
        self, requests_mock: req_mock.Mocker, output_directory: Optional[str], expected_files: List[str]
    ):
        url = host.endpoint(f"/v2/assets/{constants.ASSET_ID}/metadata")
        unpacking = len(expected_files) > 1
        requests_mock.get(url=url, json=self.asset_info)
        asset_obj = asset.Asset(asset_id=constants.ASSET_ID)
        requests_mock.post(
            url=f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID}/download-url",
            json={"url": constants.DOWNLOAD_URL},
        )
        download_files = asset_obj.download(output_directory, unpacking=unpacking)
        assert len(download_files) == len(expected_files)
        assert all([pathlib.Path(p).exists() and pathlib.Path(p).name in expected_files for p in download_files])
        assert asset_obj.results == download_files

    def test_should_download_stac_assets(
        self, requests_mock: req_mock.Mocker, output_directory: Optional[str], expected_stac_files: str
    ):
        url = host.endpoint(f"/v2/assets/{constants.ASSET_ID}/metadata")
        requests_mock.get(url=url, json=self.asset_info)
        asset_obj = asset.Asset(asset_id=constants.ASSET_ID)
        requests_mock.post(
            url=f"{constants.API_HOST}/v2/assets/{constants.STAC_ASSET_ID}/download-url",
            json={"url": constants.STAC_ASSET_URL},
        )
        out_path = asset_obj.download_stac_asset(
            pystac.Asset(href=constants.STAC_ASSET_HREF, roles=["data"]), output_directory
        )
        assert out_path.exists()
        assert out_path.name == expected_stac_files


class TestStacMetadata:
    def test_should_get_stac_items_with_retries(self, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(
            constants.URL_STAC_SEARCH,
            [{"status_code": 401}, {"json": constants.STAC_SEARCH_RESPONSE}],
        )
        asset_obj = asset.Asset(asset_info={"id": constants.ASSET_ID})
        expected = pystac.ItemCollection.from_dict(constants.STAC_SEARCH_RESPONSE)
        assert asset_obj.stac_items.to_dict() == expected.to_dict()

    def test_fails_to_get_stac_items_after_retries(self, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(constants.URL_STAC_SEARCH, status_code=401)
        asset_obj = asset.Asset(asset_info={"id": constants.ASSET_ID})
        with pytest.raises(ValueError):
            _ = asset_obj.stac_items

    def test_should_get_stac_info_with_retries(self, requests_mock: req_mock.Mocker):
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
        asset_obj = asset.Asset(asset_info={"id": constants.ASSET_ID})
        assert asset_obj.stac_info.to_dict() == expected.to_dict()

    @pytest.mark.parametrize(
        "response",
        [
            {"status_code": 401},
            {"json": {"type": "FeatureCollection", "features": []}},
        ],
    )
    def test_fails_to_get_stac_info_after_retries(self, requests_mock: req_mock.Mocker, response: dict):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        requests_mock.post(constants.URL_STAC_SEARCH, [response])
        asset_obj = asset.Asset(asset_info={"id": constants.ASSET_ID})
        with pytest.raises(Exception):
            _ = asset_obj.stac_info


class TestAssetUpdateMetadata:
    asset_info = {"id": constants.ASSET_ID, "title": "title", "tags": ["tag1"]}
    endpoint_url = f"{constants.API_HOST}/v2/assets/{constants.ASSET_ID}/metadata"

    @pytest.mark.parametrize("title", [None, "new-title"])
    @pytest.mark.parametrize("tags", [None, [], ["tag1", "tag2"]])
    def test_should_update_metadata(
        self,
        requests_mock: req_mock.Mocker,
        title: Optional[str],
        tags: Optional[List[str]],
    ):
        asset_obj = asset.Asset(asset_info=self.asset_info)
        update_payload = {"title": title, "tags": tags}
        expected_info = {**self.asset_info, **update_payload}
        requests_mock.post(
            url=self.endpoint_url,
            json=expected_info,
            additional_matcher=helpers.match_request_body(update_payload),
        )
        assert asset_obj.update_metadata(title=title, tags=tags) == expected_info

    def test_should_not_update_title_if_not_provided(self, requests_mock: req_mock.Mocker):
        asset_obj = asset.Asset(asset_info=self.asset_info)
        tags = ["tag1", "tag2"]
        update_payload = {"tags": tags}
        expected_info = {**self.asset_info, **update_payload}
        requests_mock.post(
            url=self.endpoint_url,
            json=expected_info,
            additional_matcher=helpers.match_request_body(update_payload),
        )
        assert asset_obj.update_metadata(tags=tags) == expected_info

    def test_should_not_update_tags_if_not_provided(self, requests_mock: req_mock.Mocker):
        asset_obj = asset.Asset(asset_info=self.asset_info)
        title = "new-title"
        update_payload = {"title": title}
        expected_info = {**self.asset_info, **update_payload}
        requests_mock.post(
            url=self.endpoint_url,
            json=expected_info,
            additional_matcher=helpers.match_request_body(update_payload),
        )
        assert asset_obj.update_metadata(title=title) == expected_info
