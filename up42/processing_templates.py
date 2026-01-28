import abc
import dataclasses
from typing import ClassVar, List, Optional, Union

import pystac
import requests

from up42 import base, host, processing


class JobTemplate:
    session = base.Session()
    process_id: ClassVar[str]
    workspace_id: Union[str, base.WorkspaceId]
    errors: set[processing.ValidationError] = set()
    process_description: dict = {}

    @property
    @abc.abstractmethod
    def inputs(self) -> dict:
        pass

    def __post_init__(self):
        self.__validate()
        if self.is_valid:
            self.__evaluate()

    def __validate(self):
        self.errors = self.__validate_process_exists() or self.__validate_eula() or self.__validate_inputs()

    def __validate_process_exists(self) -> set[processing.ValidationError]:
        process_url = host.endpoint(f"/v2/processing/processes/{self.process_id}")
        try:
            self.process_description = self.session.get(process_url).json()
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                return {
                    processing.ValidationError(
                        name="ProcessNotFound",
                        message=f"The process {self.process_id} does not exist.",
                    )
                }
            else:
                raise err
        return set()

    def __validate_eula(self) -> set[processing.ValidationError]:
        eula_id = next(
            parameter["value"][0]
            for parameter in self.process_description["additionalParameters"]["parameters"]
            if parameter["name"] == "eula-id"
        )
        eula_url = host.endpoint(f"/v2/eulas/{eula_id}")
        eula = self.session.get(eula_url).json()
        if not eula["isAccepted"]:
            return {
                processing.ValidationError(
                    name="EulaNotAccepted",
                    message=f"EULA for the process {self.process_id} not accepted.",
                )
            }
        return set()

    def __validate_inputs(self) -> set[processing.ValidationError]:
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/validation")
        try:
            _ = self.session.post(url, json={"inputs": self.inputs})
        except requests.HTTPError as err:
            if (status_code := err.response.status_code) in (400, 422):
                if status_code == 400:
                    return {
                        processing.ValidationError(
                            name="InvalidSchema",
                            message=err.response.json()["schema-error"],
                        )
                    }
                if status_code == 422:
                    errors = err.response.json()["errors"]
                    return {processing.ValidationError(**error) for error in errors}
            else:
                raise err
        return set()

    def __evaluate(self):
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/cost")
        payload = self.session.post(url, json={"inputs": self.inputs}).json()
        self.cost = processing.Cost(
            strategy=payload["pricingStrategy"],
            credits=payload["totalCredits"],
            size=payload.get("totalSize"),
            unit=payload.get("unit"),
        )

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def execute(self) -> processing.Job:
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/execution")
        job_metadata = self.session.post(
            url, params={"workspaceId": self.workspace_id}, json={"inputs": self.inputs}
        ).json()
        return processing.Job.from_metadata(job_metadata)


@dataclasses.dataclass
class SingleItemJobTemplate(JobTemplate):
    title: str
    item: pystac.Item

    @property
    def inputs(self) -> dict:
        return {"title": self.title, "item": self.item.get_self_href()}


@dataclasses.dataclass
class MultiItemJobTemplate(JobTemplate):
    title: str
    items: List[pystac.Item]

    @property
    def inputs(self) -> dict:
        return {
            "title": self.title,
            "items": [item.get_self_href() for item in self.items],
        }


# TODO: drop these with Python 3.10 kw_only=True data classes
@dataclasses.dataclass
class WorkspaceIdSingleItemTemplate(SingleItemJobTemplate):
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


@dataclasses.dataclass
class WorkspaceIdMultiItemTemplate(MultiItemJobTemplate):
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


@dataclasses.dataclass
class DetectionBuildingsSpacept(WorkspaceIdSingleItemTemplate):
    process_id = "detection-buildings-spacept"


@dataclasses.dataclass
class DetectionTreesSpacept(WorkspaceIdSingleItemTemplate):
    process_id = "detection-trees-spacept"


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
class UpsamplingNS(WorkspaceIdSingleItemTemplate):
    process_id = "upsampling-ns"


@dataclasses.dataclass
class UpsamplingNSSentinel(WorkspaceIdSingleItemTemplate):
    process_id = "upsampling-ns-sentinel"


@dataclasses.dataclass
class TrueColorConversion(WorkspaceIdSingleItemTemplate):
    process_id = "true-color-conversion"


@dataclasses.dataclass
class SimularityJobTemplate(JobTemplate):
    title: str
    source_item: pystac.Item
    reference_item: pystac.Item
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())

    @property
    def inputs(self) -> dict:
        return {
            "title": self.title,
            "sourceItem": self.source_item.get_self_href(),
            "referenceItem": self.reference_item.get_self_href(),
        }


@dataclasses.dataclass
class CoregistrationSimularity(SimularityJobTemplate):
    process_id = "coregistration-simularity"


@dataclasses.dataclass
class DetectionChangeSimularity(SimularityJobTemplate):
    process_id = "detection-change-simularity"
    sensitivity: int = 2

    @property
    def inputs(self):
        sensitivity = {"sensitivity": self.sensitivity}
        return {**super().inputs, **sensitivity}


@dataclasses.dataclass
class GreyWeight:
    band: str
    weight: float


@dataclasses.dataclass
class Pansharpening(SingleItemJobTemplate):
    grey_weights: Optional[List[GreyWeight]] = None
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
    process_id = "pansharpening"

    @property
    def inputs(self):
        weights = (
            {"greyWeights": [dataclasses.asdict(weight) for weight in self.grey_weights]} if self.grey_weights else {}
        )
        return {**super().inputs, **weights}
