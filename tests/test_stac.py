import datetime
import uuid

import pystac
import pytest
import requests_mock as req_mock

from tests import constants, helpers
from up42 import stac, utils


@pytest.fixture(autouse=True)
def extend_stac_objects():
    stac.extend()


ASSET_ID = "asset-id"
DOWNLOAD_URL = f"{constants.API_HOST}/abcdef.tgz"
STAC_ASSET_HREF = f"{constants.API_HOST}/v2/assets/{ASSET_ID}"


class TestFileProvider:
    def test_fails_as_class_property(self):
        with pytest.raises(AttributeError):
            _ = pystac.Asset.file  # type: ignore

    def test_should_provide_no_file_with_external_assets(self):
        asset = pystac.Asset(href="http://example.com", title="some-title")
        assert not asset.file  # type: ignore

    def test_should_provide_image_file_with_signed_url(self, requests_mock: req_mock.Mocker):
        requests_mock.post(
            url=f"{STAC_ASSET_HREF}/download-url",
            json={"url": DOWNLOAD_URL},
        )
        asset = pystac.Asset(href=STAC_ASSET_HREF)
        expected = utils.ImageFile(url=DOWNLOAD_URL)
        assert asset.file == expected  # type: ignore


class TestUpdateItem:
    def test_should_update_item_metadata(self, requests_mock: req_mock.Mocker):
        item = pystac.Item(
            id=str(uuid.uuid4()),
            collection=str(uuid.uuid4()),
            geometry=None,
            bbox=None,
            datetime=datetime.datetime.now(),
            properties={"up42-user:title": "title", "up42-user:tags": ["tag"]},
        )
        response = item.to_dict()
        response["properties"] |= {"up42-user:title": "response-title", "up42-user:tags": ["response-tags"]}
        requests_mock.patch(
            url=f"/v2/assets/stac/collections/{item.collection_id}/items/{item.id}",
            json=response,
            additional_matcher=helpers.match_request_body(
                {
                    "up42-user:title": item.properties["up42-user:title"],
                    "up42-user:tags": item.properties["up42-user:tags"],
                }
            ),
        )

        item.update()  # type: ignore

        assert item.properties["up42-user:title"] == response["properties"]["up42-user:title"]
        assert item.properties["up42-user:tags"] == response["properties"]["up42-user:tags"]
