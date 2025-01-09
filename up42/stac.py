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


def extend():
    pystac.Asset.file = FileProvider()  # type: ignore
    update_item = UpdateItem()
    pystac.Item.update = lambda self: update_item(self)  # type: ignore # pylint: disable=unnecessary-lambda
