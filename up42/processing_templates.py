import dataclasses
from typing import List, Optional, Union

from up42 import base, processing


# TODO: drop these with Python 3.10 kw_only=True data classes
@dataclasses.dataclass
class WorkspaceIdSingleItemTemplate(processing.SingleItemJobTemplate):
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


@dataclasses.dataclass
class WorkspaceIdMultiItemTemplate(processing.MultiItemJobTemplate):
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


@dataclasses.dataclass
class DetectionBuildingsSpacept(WorkspaceIdSingleItemTemplate):
    process_id = "detection-buildings-spacept"


@dataclasses.dataclass
class DetectionTreesSpacept(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trees-spacept"


@dataclasses.dataclass
class DetectionTreesHeightsSpacept(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trees-heights-spacept"


@dataclasses.dataclass
class DetectionShadowsSpacept(WorkspaceIdSingleItemTemplate):
    process_id = "detection-shadows-spacept"


@dataclasses.dataclass
class DetectionShipsAirbus(WorkspaceIdSingleItemTemplate):
    process_id = "detection-ships-airbus"


@dataclasses.dataclass
class DetectionWindTurbinesAirbus(WorkspaceIdSingleItemTemplate):
    process_id = "detection-wind-turbines-airbus"


@dataclasses.dataclass
class DetectionStorageTanksAirbus(WorkspaceIdSingleItemTemplate):
    process_id = "detection-storage-tanks-airbus"


@dataclasses.dataclass
class DetectionTrucksOI(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trucks-oi"


@dataclasses.dataclass
class DetectionCarsOI(WorkspaceIdSingleItemTemplate):
    process_id = "detection-cars-oi"


@dataclasses.dataclass
class DetectionAircraftOI(WorkspaceIdSingleItemTemplate):
    process_id = "detection-aircraft-oi"


@dataclasses.dataclass
class DetectionChangeSpacept(WorkspaceIdMultiItemTemplate):
    process_id = "detection-change-spacept"


@dataclasses.dataclass
class DetectionChangePleiadesHyperverge(WorkspaceIdMultiItemTemplate):
    process_id = "detection-change-pleiades-hyperverge"


@dataclasses.dataclass
class DetectionChangeSPOTHyperverge(WorkspaceIdMultiItemTemplate):
    process_id = "detection-change-spot-hyperverge"


@dataclasses.dataclass
class UpsamplingNS(processing.SingleItemJobTemplate):
    ned: bool = False
    rgb: bool = True
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
    process_id = "upsampling-ns"

    @property
    def inputs(self):
        return {
            **super().inputs,
            "NED": self.ned,
            "RGB": self.rgb,
        }


@dataclasses.dataclass
class GreyWeight:
    band: str
    weight: float


@dataclasses.dataclass
class Pansharpening(processing.SingleItemJobTemplate):
    grey_weights: Optional[List[GreyWeight]] = None
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
    process_id = "pansharpening"

    @property
    def inputs(self):
        weights = (
            {"greyWeights": [dataclasses.asdict(weight) for weight in self.grey_weights]} if self.grey_weights else {}
        )
        return {**super().inputs, **weights}
