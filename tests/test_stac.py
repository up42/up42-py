import datetime as dt
import uuid
from unittest import mock

import pystac
import pytest

from tests import constants
from up42 import stac


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


EXTENSIONS = {
    "up42-user:title": "title",
    "up42-user:tags": ["tag"],
    "up42-product:product_id": "product-id",
    "up42-product:collection_name": "collection-name",
    "up42-product:modality": "modality",
    "up42-order:id": "order-id",
    "up42-system:asset_id": "asset-id",
    "up42-system:account_id": "account-id",
    "up42-system:workspace_id": "workspace-id",
    "up42-system:job_id": "job-id",
    "up42-system:source": "source",
    "up42-system:metadata_version": "metadata-version",
}

MAPPING = [
    ("title", "up42-user:title"),
    ("tags", "up42-user:tags"),
    ("product_id", "up42-product:product_id"),
    ("collection_name", "up42-product:collection_name"),
    ("modality", "up42-product:modality"),
    ("order_id", "up42-order:id"),
    ("asset_id", "up42-system:asset_id"),
    ("account_id", "up42-system:account_id"),
    ("workspace_id", "up42-system:workspace_id"),
    ("job_id", "up42-system:job_id"),
    ("source", "up42-system:source"),
    ("metadata_version", "up42-system:metadata_version"),
]


class TestUp42ExtensionProvider:
    item = pystac.Item(
        id=str(uuid.uuid4()),
        collection=str(uuid.uuid4()),
        geometry=None,
        bbox=None,
        datetime=dt.datetime.now(),
        properties=EXTENSIONS,
    )
    collection = pystac.Collection(
        id=str(uuid.uuid4()),
        description="",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent(bboxes=[[1.0, 2.0, 3.0, 4.0]]),
            temporal=pystac.TemporalExtent(intervals=[[dt.datetime.now(), None]]),
        ),
        extra_fields=EXTENSIONS,
    )

    @pytest.mark.parametrize("entity_class", [pystac.Item, pystac.Collection])
    def test_fails_as_class_property(self, entity_class):
        with pytest.raises(AttributeError):
            _ = entity_class.up42  # type: ignore

    @pytest.mark.parametrize("entity", [item, collection])
    @pytest.mark.parametrize("attribute, key", MAPPING)
    def test_should_provide_up42_extensions(self, entity, attribute, key):
        assert getattr(entity.up42, attribute) == EXTENSIONS[key]  # type: ignore

    @pytest.mark.parametrize(
        "entity, entity_dict",
        [(item, item.properties), (collection, collection.extra_fields)],
    )
    @pytest.mark.parametrize("attribute, key", MAPPING)
    def test_should_set_up42_extension(self, entity, entity_dict, attribute, key):
        new_value = "new-value"
        setattr(entity.up42, attribute, new_value)  # type: ignore
        assert entity_dict[key] == new_value


class TestBulkDeletion:
    items = [
        pystac.Item(
            id=f"item-id-{i}",
            collection="collection-id",
            geometry=None,
            bbox=None,
            datetime=dt.datetime.now(),
            properties={},
        )
        for i in range(2)
    ]
    collection_with_all_items = pystac.Collection(
        id="collection-id",
        description="",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent(bboxes=[[1.0, 2.0, 3.0, 4.0]]),
            temporal=pystac.TemporalExtent(intervals=[[dt.datetime.now(), None]]),
        ),
        extra_fields={},
    )
    collection_with_all_items.add_items(items)

    def test_should_raise_and_not_submit_when_missing_items(self):
        mock_stac_client = mock.Mock()
        mock_stac_client.get_items.return_value = iter([self.items[0]])
        mock_stac_client.get_collection.return_value = self.collection_with_all_items
        bulk_deletion = stac.BulkDeletion(self.items[0].id)
        bulk_deletion.stac_client = mock_stac_client
        with pytest.raises(stac.IncompleteCollectionDeletionError):
            bulk_deletion.delete()

    def test_should_delete_staged_items(self, requests_mock: req_mock.Mocker):
        requests_mock.delete(
            url=f"/v2/assets/stac/collections/{self.collection_with_all_items.id}",
            status_code=204,
        )
        mock_stac_client = mock.Mock()
        mock_stac_client.get_items.return_value = iter(self.items)
        mock_stac_client.get_collection.return_value = self.collection_with_all_items

        bulk_deletion = stac.BulkDeletion(self.items[0].id, self.items[1].id)
        bulk_deletion.stac_client = mock_stac_client

        bulk_deletion.delete()
        assert requests_mock.request_history[0].method == "DELETE"
