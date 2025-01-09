import datetime as dt
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
            datetime=dt.datetime.now(),
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


extensions = {
    "up42-user:title": "title",
    "up42-user:tags": ["tag"],
    "up42-product:product_id": "product-id",
    "up42-product:collection_name": "collection-name",
    "up42-product:modality": "modality",
    "up42-order:order_id": "order-id",
    "up42-system:asset_id": "asset-id",
    "up42-system:account_id": "account-id",
    "up42-system:workspace_id": "workspace-id",
    "up42-system:job_id": "job-id",
    "up42-system:source": "source",
    "up42-system:metadata_version": "metadata-version",
}


class TestUp42ExtensionProvider:
    @pytest.mark.parametrize("entity_class", [pystac.Item, pystac.Collection])
    def test_fails_as_class_property(self, entity_class):
        with pytest.raises(AttributeError):
            _ = entity_class.up42  # type: ignore

    @pytest.mark.parametrize(
        "entity",
        [
            pystac.Item(
                id=str(uuid.uuid4()),
                collection=str(uuid.uuid4()),
                geometry=None,
                bbox=None,
                datetime=dt.datetime.now(),
                properties=extensions,
            ),
            pystac.Collection(
                id=str(uuid.uuid4()),
                description="",
                extent=pystac.Extent(
                    spatial=pystac.SpatialExtent(bboxes=[[1.0, 2.0, 3.0, 4.0]]),
                    temporal=pystac.TemporalExtent(intervals=[[dt.datetime.now(), None]]),
                ),
                extra_fields=extensions,
            ),
        ],
    )
    def test_should_provide_up42_extensions(self, entity):
        assert entity.up42.title == extensions["up42-user:title"]  # type: ignore
        assert entity.up42.tags == extensions["up42-user:tags"]  # type: ignore
        assert entity.up42.product_id == extensions["up42-product:product_id"]  # type: ignore
        assert entity.up42.collection_name == extensions["up42-product:collection_name"]  # type: ignore
        assert entity.up42.modality == extensions["up42-product:modality"]  # type: ignore
        assert entity.up42.order_id == extensions["up42-order:order_id"]  # type: ignore
        assert entity.up42.asset_id == extensions["up42-system:asset_id"]  # type: ignore
        assert entity.up42.account_id == extensions["up42-system:account_id"]  # type: ignore
        assert entity.up42.workspace_id == extensions["up42-system:workspace_id"]  # type: ignore
        assert entity.up42.job_id == extensions["up42-system:job_id"]  # type: ignore
        assert entity.up42.source == extensions["up42-system:source"]  # type: ignore
        assert entity.up42.metadata_version == extensions["up42-system:metadata_version"]  # type: ignore
