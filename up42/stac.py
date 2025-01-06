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

    def __call__(self, instance):
        url = host.endpoint(f"/v2/assets/stac/collections/{instance.collection_id}/items/{instance.id}")
        response = self.session.patch(
            url=url,
            json={
                "up42-user:title": instance.properties["up42-user:title"],
                "up42-user:tags": instance.properties["up42-user:tags"],
            },
        ).json()
        instance.properties.update(
            {"up42-user:title": response["up42-user:title"], "up42-user:tags": response["up42-user:tags"]}
        )


def extend():
    pystac.Asset.file = FileProvider()  # type: ignore
    update_item = UpdateItem()
    pystac.Item.update = lambda self: update_item(self)  # type: ignore # pylint: disable=unnecessary-lambda
