import datetime
import pathlib
from typing import List, Optional

import pystac
import pytest
import requests_mock as req_mock

from tests import constants, helpers
from up42 import asset

ASSET_ID = "363f89c1-3586-4b14-9a49-03a890c3b593"
DOWNLOAD_URL = f"{constants.API_HOST}/abcdef.tgz"
STAC_FILE = "stac_file.tiff"
STAC_ASSET_URL = "https://example.com/some-random-path"
STAC_ASSET_HREF = f"{constants.API_HOST}/v2/assets/stac-id"
STAC_COLLECTION_ID = "e459db4c-3b9d-4aa1-8931-5df2517b49ba"
STAC_SEARCH_RESPONSE = {
    "type": "FeatureCollection",
    "features": [
        {
            "assets": {"data": {"href": "https://api.up42.com/v2/assets/01ad657e-12f7-4046-a94c-abc90d86106a"}},
            "links": [
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6/"
                    "items/e986e18a-0392-4b82-93c9-7a0af15846d0",
                    "rel": "self",
                    "type": "application/geo+json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
                    "rel": "parent",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
                    "rel": "collection",
                    "type": "application/json",
                },
                {
                    "href": constants.URL_STAC_CATALOG,
                    "rel": "root",
                    "type": "application/json",
                    "title": "UP42 Storage",
                },
            ],
            "stac_extensions": [
                "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                "https://api.up42.com/stac-extensions/up42-product/v1.0.0/schema.json",
            ],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [52.4941111111112, 13.4025555555556],
                        [52.4941111111112, 13.4111666666667],
                        [52.4911111111112, 13.4111666666667],
                        [52.4911111111112, 13.4025555555556],
                        [52.4941111111112, 13.4025555555556],
                        [52.4941111111112, 13.4025555555556],
                    ]
                ],
            },
            "bbox": [
                52.4911111111112,
                13.4025555555556,
                52.4941111111112,
                13.4111666666667,
            ],
            "properties": {
                "up42-system:asset_id": ASSET_ID,
                "gsd": 9.118863577837482,
                "datetime": "2021-05-31T09:51:52.100000+00:00",
                "platform": "SPOT-7",
                "proj:epsg": 4326,
                "end_datetime": "2021-05-31T09:51:52.100000+00:00",
                "eo:cloud_cover": 0.0,
                "start_datetime": "2021-05-31T09:51:52.100000+00:00",
                "up42-system:workspace_id": "7d1cf222-1fa7-468c-a93a-3e3188875997",
                "up42-product:collection_name": "Collection No 1",
            },
            "type": "Feature",
            "stac_version": "1.0.0",
            "id": "e986e18a-0392-4b82-93c9-7a0af15846d0",
            "collection": STAC_COLLECTION_ID,
        }
    ],
}


class TestAsset:
    asset_info = {"id": ASSET_ID, "other": "data"}

    @pytest.fixture(params=["output_dir", "no_output_dir"])
    def output_directory(self, request, tmp_path) -> Optional[str]:
        return tmp_path if request.param == "output_dir" else None

    @pytest.fixture(params=["unpack", "no_unpack"])
    def asset_files(self, requests_mock: req_mock.Mocker, request) -> set[str]:
        sample_tgz = pathlib.Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
        with open(sample_tgz, "rb") as src_tgz:
            requests_mock.get(
                url=DOWNLOAD_URL,
                content=src_tgz.read(),
            )
            return (
                {
                    "7e17f023-a8e3-43bd-aaac-5bbef749c7f4_0-0.tif",
                    "data.json",
                }
                if request.param == "unpack"
                else {"output.tgz"}
            )

    def test_should_delegate_repr_to_info(self):
        assert repr(asset.Asset(asset_info=self.asset_info)) == repr(self.asset_info)

    def test_should_initialize(self, requests_mock: req_mock.Mocker):
        url = f"{constants.API_HOST}/v2/assets/{ASSET_ID}/metadata"
        requests_mock.get(url=url, json=self.asset_info)
        assert asset.Asset(asset_id=ASSET_ID).info == self.asset_info

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
                ASSET_ID,
                {"id": ASSET_ID},
                "asset_id and asset_info cannot be provided simultaneously.",
            ),
        ],
        ids=[
            "Both asset_id and asset_info provided",
            "Neither asset_id and asset_info provided",
        ],
    )
    def test_fails_to_initialize_with_concurrent_or_empty_info_id(
        self, asset_id: Optional[str], asset_info: Optional[dict], expected_error: str
    ):
        with pytest.raises(ValueError, match=expected_error):
            asset.Asset(asset_id=asset_id, asset_info=asset_info)

    def test_should_download_expected_files(
        self,
        requests_mock: req_mock.Mocker,
        output_directory: Optional[str],
        asset_files: set[str],
    ):
        url = f"{constants.API_HOST}/v2/assets/{ASSET_ID}/metadata"
        unpacking = len(asset_files) > 1
        requests_mock.get(url=url, json=self.asset_info)
        asset_obj = asset.Asset(asset_id=ASSET_ID)
        requests_mock.post(
            url=f"{constants.API_HOST}/v2/assets/{ASSET_ID}/download-url",
            json={"url": DOWNLOAD_URL},
        )
        downloaded_files = asset_obj.download(output_directory, unpacking=unpacking)
        paths = map(pathlib.Path, downloaded_files)
        assert set(path.name for path in paths) == asset_files
        assert all(path.exists() for path in paths)

    def test_get_stac_download_url(self, requests_mock: req_mock.Mocker):
        url = f"{constants.API_HOST}/v2/assets/{ASSET_ID}/metadata"
        requests_mock.get(url=url, json=self.asset_info)
        asset_obj = asset.Asset(asset_id=ASSET_ID)
        requests_mock.post(
            url=f"{STAC_ASSET_HREF}/download-url",
            json={"url": STAC_ASSET_URL},
        )
        assert STAC_ASSET_URL == asset_obj.get_stac_asset_url(pystac.Asset(href=STAC_ASSET_HREF))

    @pytest.mark.parametrize(
        "stac_url, stac_file",
        [
            (
                f"{STAC_ASSET_URL}?response-content-disposition=_filename={STAC_FILE}",
                STAC_FILE,
            ),
            (
                STAC_ASSET_URL,
                "output",
            ),
        ],
        ids=[
            "URL STAC format",
            "Another format",
        ],
    )
    def test_should_download_stac_asset(
        self,
        requests_mock: req_mock.Mocker,
        output_directory: Optional[str],
        stac_url: str,
        stac_file: str,
    ):
        url = f"{constants.API_HOST}/v2/assets/{ASSET_ID}/metadata"
        requests_mock.get(url=url, json=self.asset_info)
        asset_obj = asset.Asset(asset_id=ASSET_ID)
        content = b"some-content"
        requests_mock.get(url=stac_url, content=content)
        requests_mock.post(
            url=f"{STAC_ASSET_HREF}/download-url",
            json={"url": stac_url},
        )
        out_path = asset_obj.download_stac_asset(pystac.Asset(href=STAC_ASSET_HREF, title="stac"), output_directory)
        assert out_path.exists()
        assert out_path.name == stac_file
        assert out_path.read_bytes() == content

    class TestStacMetadata:
        def test_should_get_stac_items_with_retries(self, requests_mock: req_mock.Mocker):
            requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
            requests_mock.post(
                constants.URL_STAC_SEARCH,
                [{"status_code": 401}, {"json": STAC_SEARCH_RESPONSE}],
            )
            asset_obj = asset.Asset(asset_info={"id": ASSET_ID})
            expected = pystac.ItemCollection.from_dict(STAC_SEARCH_RESPONSE)
            assert asset_obj.stac_items.to_dict() == expected.to_dict()

        def test_fails_to_get_stac_items_after_retries(self, requests_mock: req_mock.Mocker):
            requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
            requests_mock.post(constants.URL_STAC_SEARCH, status_code=401)
            asset_obj = asset.Asset(asset_info={"id": ASSET_ID})
            with pytest.raises(ValueError):
                _ = asset_obj.stac_items

        def test_should_get_stac_info_with_retries(self, requests_mock: req_mock.Mocker):
            requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
            requests_mock.post(
                constants.URL_STAC_SEARCH,
                [{"status_code": 401}, {"json": STAC_SEARCH_RESPONSE}],
            )
            expected = pystac.Collection(
                id="up42-storage",
                description="UP42 Storage STAC API",
                extra_fields={"up42-system:asset_id": ASSET_ID},
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
                url=f"{constants.API_HOST}/v2/assets/stac/collections/{STAC_COLLECTION_ID}",
                json=expected.to_dict(),
            )
            asset_obj = asset.Asset(asset_info={"id": ASSET_ID})
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
            asset_obj = asset.Asset(asset_info={"id": ASSET_ID})
            with pytest.raises(Exception):
                _ = asset_obj.stac_info

    class TestAssetUpdateMetadata:
        asset_info = {"id": ASSET_ID, "title": "title", "tags": ["tag1"]}
        endpoint_url = f"{constants.API_HOST}/v2/assets/{ASSET_ID}/metadata"

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
