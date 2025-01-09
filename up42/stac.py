import dataclasses
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


@dataclasses.dataclass
class Up42Extension:
    title: str | None
    tags: list[str] | None
    product_id: str | None
    collection_name: str | None
    modality: str | None
    order_id: str | None
    asset_id: str | None
    account_id: str | None
    workspace_id: str | None
    job_id: str | None
    source: str | None
    metadata_version: str | None

    def __init__(self, properties: dict):
        self.title = properties.get("up42-user:title")
        self.tags = properties.get("up42-user:tags")
        self.product_id = properties.get("up42-product:product_id")
        self.collection_name = properties.get("up42-product:collection_name")
        self.modality = properties.get("up42-product:modality")
        self.order_id = properties.get("up42-order:order_id")
        self.asset_id = properties.get("up42-system:asset_id")
        self.account_id = properties.get("up42-system:account_id")
        self.workspace_id = properties.get("up42-system:workspace_id")
        self.job_id = properties.get("up42-system:job_id")
        self.source = properties.get("up42-system:source")
        self.metadata_version = properties.get("up42-system:metadata_version")


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
