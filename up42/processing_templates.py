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


@dataclasses.dataclass
class SpaceptAugmentation(processing.SingleItemJobTemplate):
    denoising_factor: int = 0
    colour_denoising_factor: int = 10
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
    process_id = "augmentation-spacept"

    @property
    def inputs(self):
        return {
            **super().inputs,
            "denoising_factor": self.denoising_factor,
            "colour_denoising_factor": self.colour_denoising_factor,
        }


@dataclasses.dataclass
class NSUpsamling(processing.SingleItemJobTemplate):
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
