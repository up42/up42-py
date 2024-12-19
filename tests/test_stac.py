import pystac
import pytest
import requests_mock as req_mock

from tests import constants
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
        title = "some-title"
        asset = pystac.Asset(href=STAC_ASSET_HREF, title=title)
        expected = utils.ImageFile(url=DOWNLOAD_URL, file_name=title)
        assert asset.file == expected  # type: ignore
