import abc
import dataclasses
import datetime
import enum
from typing import ClassVar, List, Optional, TypedDict, Union

import pystac
import requests

from up42 import base, host


@dataclasses.dataclass(frozen=True)
class ValidationError:
    message: str
    name: str


CostType = Union[int, float, "Cost"]


@dataclasses.dataclass(frozen=True)
class Cost:
    strategy: str
    credits: int
    size: Optional[int] = None
    unit: Optional[str] = None

    def __le__(self, other: CostType):
        if isinstance(other, Cost):
            return self.credits <= other.credits
        else:
            return self.credits <= other

    def __lt__(self, other: CostType):
        if isinstance(other, Cost):
            return self.credits < other.credits
        else:
            return self.credits < other

    def __ge__(self, other: CostType):
        return not self < other

    def __gt__(self, other: CostType):
        return not self <= other


class JobTemplate:
    session = base.Session()
    process_id: ClassVar[str]
    workspace_id: Union[str, base.WorkspaceId]
    errors: set[ValidationError] = set()

    @property
    @abc.abstractmethod
    def inputs(self) -> dict:
        pass

    def __post_init__(self):
        self.__validate()
        if self.is_valid:
            self.__evaluate()

    def __validate(self) -> None:
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/validation")
        try:
            _ = self.session.post(url, json={"inputs": self.inputs})
        except requests.HTTPError as err:
            if (status_code := err.response.status_code) in (400, 422):
                if status_code == 400:
                    self.errors = {
                        ValidationError(
                            name="InvalidSchema",
                            message=err.response.json()["schema-error"],
                        )
                    }
                if status_code == 422:
                    errors = err.response.json()["errors"]
                    self.errors = {ValidationError(**error) for error in errors}
            else:
                raise err

    def __evaluate(self):
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/cost")
        payload = self.session.post(url, json={"inputs": self.inputs}).json()
        self.cost = Cost(
            strategy=payload["pricingStrategy"],
            credits=payload["totalCredits"],
            size=payload.get("totalSize"),
            unit=payload.get("unit"),
        )

    @property
    def is_valid(self) -> bool:
        return not self.errors

    # TODO: def create_job(self) -> Job:


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


class JobStatuses(enum.Enum):
    CREATED = "created"
    VALID = "valid"
    INVALID = "invalid"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CAPTURED = "captured"
    RELEASED = "released"


class JobMetadata(TypedDict):
    processID: Optional[str]  # pylint: disable=invalid-name
    jobID: str  # pylint: disable=invalid-name
    accountID: Optional[str]  # pylint: disable=invalid-name
    workspaceID: Optional[str]  # pylint: disable=invalid-name
    definition: dict
    status: str
    created: Optional[str]
    started: Optional[str]
    finished: Optional[str]
    updated: Optional[str]


@dataclasses.dataclass
class Job:
    session = base.Session()
    process_id: Optional[str]
    id: str
    account_id: Optional[str]
    workspace_id: Optional[str]
    definition: dict
    status: JobStatuses
    created: Optional[datetime.datetime] = None
    started: Optional[datetime.datetime] = None
    finished: Optional[datetime.datetime] = None
    updated: Optional[datetime.datetime] = None

    @staticmethod
    def from_metadata(metadata: JobMetadata) -> "Job":
        created = datetime.datetime.fromisoformat(metadata["created"]) if metadata["created"] else None
        started = datetime.datetime.fromisoformat(metadata["started"]) if metadata["started"] else None
        finished = datetime.datetime.fromisoformat(metadata["finished"]) if metadata["finished"] else None
        updated = datetime.datetime.fromisoformat(metadata["updated"]) if metadata["updated"] else None
        return Job(
            process_id=metadata["processID"],
            id=metadata["jobID"],
            account_id=metadata["accountID"],
            workspace_id=metadata["workspaceID"],
            definition=metadata["definition"],
            status=JobStatuses(metadata["status"]),
            created=created,
            started=started,
            finished=finished,
            updated=updated,
        )

    @classmethod
    def get(cls, job_id: str) -> "Job":
        url = host.endpoint(f"/v2/processing/jobs/{job_id}")
        metadata = cls.session.get(url).json()
        return cls.from_metadata(metadata)
