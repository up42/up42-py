from typing import Optional, Union

import pystac

from up42 import base, host, utils


class InvalidUp42Asset(ValueError):
    pass


class IncompleteCollectionDeletionError(ValueError):
    """Raised when attempting to delete a collection but not all items in the collection are included."""

    pass


class FileProvider:
    session = base.Session()

    def __get__(self, obj: Optional[pystac.Asset], obj_type=None) -> Optional[utils.ImageFile]:
        if obj:
            if obj.href.startswith(host.endpoint("")):
                url = obj.href + "/download-url"
                signed_url = self.session.post(url=url).json()["url"]
                return utils.ImageFile(url=signed_url)
            else:
                return None
        else:
            raise AttributeError


UP42_USER_TITLE_KEY = "up42-user:title"
UP42_USER_TAGS_KEY = "up42-user:tags"


class UpdateItem:
    session = base.Session()

    def __call__(self, item):
        url = host.endpoint(f"/v2/assets/stac/collections/{item.collection_id}/items/{item.id}")
        response = pystac.Item.from_dict(
            self.session.patch(
                url=url,
                json={
                    UP42_USER_TITLE_KEY: item.properties.get(UP42_USER_TITLE_KEY),
                    UP42_USER_TAGS_KEY: item.properties.get(UP42_USER_TAGS_KEY),
                },
            ).json()
        )
        for key, value in vars(response).items():
            setattr(item, key, value)


class Up42ExtensionProperty:
    key: str

    def __init__(self, key):
        self.key = key

    def __get__(self, obj, obj_type=None):
        return obj._reference.get(self.key)

    def __set__(self, obj, value):
        obj._reference[self.key] = value


class Up42Extension:
    title = Up42ExtensionProperty("up42-user:title")
    tags = Up42ExtensionProperty("up42-user:tags")
    product_id = Up42ExtensionProperty("up42-product:product_id")
    collection_name = Up42ExtensionProperty("up42-product:collection_name")
    modality = Up42ExtensionProperty("up42-product:modality")
    order_id = Up42ExtensionProperty("up42-order:id")
    asset_id = Up42ExtensionProperty("up42-system:asset_id")
    account_id = Up42ExtensionProperty("up42-system:account_id")
    workspace_id = Up42ExtensionProperty("up42-system:workspace_id")
    job_id = Up42ExtensionProperty("up42-system:job_id")
    source = Up42ExtensionProperty("up42-system:source")
    metadata_version = Up42ExtensionProperty("up42-system:metadata_version")

    def __init__(self, reference: dict):
        self._reference = reference


class Up42ExtensionProvider:
    def __get__(self, obj: Optional[Union[pystac.Item, pystac.Collection]], obj_type=None):
        if obj:
            if obj_type == pystac.Item:
                return Up42Extension(obj.properties)  # type: ignore
            else:
                return Up42Extension(obj.extra_fields)  # type: ignore
        else:
            raise AttributeError


def extend():
    pystac.Asset.file = FileProvider()  # type: ignore

    update_item = UpdateItem()
    pystac.Item.update = lambda self: update_item(self)  # type: ignore # pylint: disable=unnecessary-lambda

    pystac.Item.up42 = Up42ExtensionProvider()  # type: ignore
    pystac.Collection.up42 = Up42ExtensionProvider()  # type: ignore


class BulkDeletion:
    session = base.Session()
    stac_client = base.StacClient()

    def __init__(self):
        self._collections: set[pystac.Collection] = set()
        self._items: set[pystac.Item] = set()

    def add(self, *item_ids: str):
        """
        Add item IDs to the collection deletion stash.
        Collections are deleted as a whole: all items in any affected collection must be included.

        Args:
            *item_ids: Individual item IDs to add for deletion
        """
        items = self.stac_client.get_items(*item_ids)

        for item in items:
            collection = item.get_parent()
            if isinstance(collection, pystac.Collection):
                self._items.add(item)
                self._collections.add(collection)

    def validate(self) -> Optional[IncompleteCollectionDeletionError]:
        for collection in self._collections:
            staged_item_ids = {item_in_collection.id for item_in_collection in collection.get_items()}
            missing_items = staged_item_ids - set(item.id for item in self._items)
            if missing_items:
                error_msg = (
                    f"Collection '{collection.id}' cannot be deleted because the following items were not included "
                    f"in the deletion request: {list(missing_items)}. "
                    f"Collections are deleted as a whole, so all {len(staged_item_ids)} items in collection "
                    f"'{collection.id}' must be explicitly added for deletion. "
                    f"Please add the missing items to your deletion request."
                )
                return IncompleteCollectionDeletionError(error_msg)
        return None

    def submit(self):
        """
        Submit the bulk deletion request. This will effectively delete all items in the collections in the stash.

        Returns:
            A dictionary mapping collection IDs to their corresponding DELETE responses.
        """
        if not self._collections:
            raise ValueError("No items to delete. Use add() to add item IDs before submitting.")

        if validation_error := self.validate():
            self._collections.clear()
            raise validation_error

        responses = {}
        for collection in self._collections:
            url = host.endpoint(f"/v2/assets/stac/collections/{collection.id}")
            response = self.session.delete(url=url)
            responses[collection.id] = response

        self._collections.clear()
        self._items.clear()
        return responses
