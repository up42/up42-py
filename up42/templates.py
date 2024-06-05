import dataclasses
from typing import Union

import pystac

from up42 import base
from up42.processing import SingleItemBaseJobTemplate


@dataclasses.dataclass(eq=True, frozen=True)
class PansharpeningJobTemplate(SingleItemBaseJobTemplate):
    item: pystac.Item
    title: str
    process_id: str = "pansharpening"
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(
        default=base.WorkspaceId()
    )
