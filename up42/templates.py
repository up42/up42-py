import dataclasses
from typing import Union

from up42 import base, processing


@dataclasses.dataclass
class WorkspaceIdSingleItemTemplate(processing.SingleItemJobTemplate):
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


@dataclasses.dataclass
class WorkspaceIdMultiItemTemplate(processing.MultiItemJobTemplate):
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


@dataclasses.dataclass
class SpaceptBuildingsDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-buildings-spacept"


@dataclasses.dataclass
class SpaceptTreesDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trees-spacept"


@dataclasses.dataclass
class SpaceptTreeHeightsDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trees-heights-spacept"


@dataclasses.dataclass
class SpaceptShadowsDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-shadows-spacept"


@dataclasses.dataclass
class AirbusShipsDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-ships-airbus"


@dataclasses.dataclass
class AirbusWindTurbinesDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-wind-turbines-airbus"


@dataclasses.dataclass
class AirbusStorageTanksDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-storage-tanks-airbus"


@dataclasses.dataclass
class OrbitalInsightTrucksDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trucks-oi"


@dataclasses.dataclass
class OrbitalInsightCarsDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-cars-oi"


@dataclasses.dataclass
class OrbitalInsightAircraftDetection(WorkspaceIdSingleItemTemplate):
    process_id = "detection-aircraft-oi"


@dataclasses.dataclass
class SpaceptChangeDetection(WorkspaceIdMultiItemTemplate):
    process_id = "detection-change-spacept"


@dataclasses.dataclass
class HypervergePleiadesChangeDetection(WorkspaceIdMultiItemTemplate):
    process_id = "detection-change-pleiades-hyperverge"


@dataclasses.dataclass
class HypervergeSpotChangeDetection(WorkspaceIdMultiItemTemplate):
    process_id = "detection-change-spot-hyperverge"
