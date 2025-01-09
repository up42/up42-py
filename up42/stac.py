from typing import Optional

import pystac

from up42 import base, host, utils


class InvalidUp42Asset(ValueError):
    pass


class FileProvider:
    session = base.Session()

    def __get__(self, obj: Optional[pystac.Asset], obj_type=None) -> Optional[utils.ImageFile]:
        if obj:
            if obj.href.startswith("https://api.up42"):
                url = obj.href + "/download-url"
                signed_url = self.session.post(url=url).json()["url"]
                return utils.ImageFile(url=signed_url)
            else:
                return None
        else:
            raise AttributeError


class UpdateItem:
    session = base.Session()

    def __call__(self, item):
        url = host.endpoint(f"/v2/assets/stac/collections/{item.collection_id}/items/{item.id}")
        response = pystac.Item.from_dict(
            self.session.patch(
                url=url,
                json={
                    "up42-user:title": item.properties.get("up42-user:title"),
                    "up42-user:tags": item.properties.get("up42-user:tags"),
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
    order_id = Up42ExtensionProperty("up42-order:order_id")
    asset_id = Up42ExtensionProperty("up42-system:asset_id")
    account_id = Up42ExtensionProperty("up42-system:account_id")
    workspace_id = Up42ExtensionProperty("up42-system:workspace_id")
    job_id = Up42ExtensionProperty("up42-system:job_id")
    source = Up42ExtensionProperty("up42-system:source")
    metadata_version = Up42ExtensionProperty("up42-system:metadata_version")

    def __init__(self, reference: dict):
        self._reference = reference


class Up42ExtensionProvider:
    def __get__(self, obj: Optional[pystac.Item | pystac.Collection], obj_type=None):
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
