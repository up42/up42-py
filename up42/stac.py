from typing import Optional

import pystac

from up42 import base, utils


class InvalidUp42Asset(ValueError):
    pass


class FileProvider:
    session = base.Session()

    def __get__(self, obj: Optional[pystac.Asset], obj_type=None) -> Optional[utils.ImageFile]:
        if obj:
            if obj.href.startswith("https://api.up42"):
                url = obj.href + "/download-url"
                signed_url = self.session.post(url=url).json()["url"]
                return utils.ImageFile(url=signed_url, session=self.session)
            else:
                return None
        else:
            raise AttributeError


def extend():
    pystac.Asset.file = FileProvider()  # type: ignore
