import dataclasses
from typing import Union

import pystac

from up42 import base, processing


@dataclasses.dataclass(eq=True, frozen=True)
class PansharpeningJobTemplate(processing.SingleItemBaseJobTemplate):
    item: pystac.Item
    title: str
    process_id: str = "pansharpening"
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
