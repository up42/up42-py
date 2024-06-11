import abc
import dataclasses
import datetime
import enum
from typing import ClassVar, List, Optional, TypedDict, Union

import pystac
import requests
import tenacity as tnc

from up42 import base, host


@dataclasses.dataclass(frozen=True)
class ValidationError:
    message: str
    name: str


class JobStatus(enum.Enum):
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
    processID: str  # pylint: disable=invalid-name
    jobID: str  # pylint: disable=invalid-name
    accountID: str  # pylint: disable=invalid-name
    workspaceID: Optional[str]  # pylint: disable=invalid-name
    definition: dict
    status: str
    created: str
    started: Optional[str]
    finished: Optional[str]
    updated: str


class UnfinishedJob(Exception):
    """Job hasn't finished yet with success or failure"""


@dataclasses.dataclass
class Job:
    session = base.Session()
    process_id: str
    id: str
    account_id: str
    workspace_id: Optional[str]
    definition: dict
    status: JobStatus
    created: datetime.datetime
    updated: datetime.datetime
    started: Optional[datetime.datetime] = None
    finished: Optional[datetime.datetime] = None

    @staticmethod
    def __to_datetime(value: Optional[str]):
        return value and datetime.datetime.fromisoformat(value.rstrip("Z"))

    @staticmethod
    def from_metadata(metadata: JobMetadata) -> "Job":
        return Job(
            process_id=metadata["processID"],
            id=metadata["jobID"],
            account_id=metadata["accountID"],
            workspace_id=metadata["workspaceID"],
            definition=metadata["definition"],
            status=JobStatus(metadata["status"]),
            created=Job.__to_datetime(metadata["created"]),
            started=Job.__to_datetime(metadata["started"]),
            finished=Job.__to_datetime(metadata["finished"]),
            updated=Job.__to_datetime(metadata["updated"]),
        )

    @classmethod
    def get(cls, job_id: str) -> "Job":
        url = host.endpoint(f"/v2/processing/jobs/{job_id}")
        metadata = cls.session.get(url).json()
        return cls.from_metadata(metadata)

    def track(self, *, wait: int = 60, retries: int = 60 * 24 * 3):
        @tnc.retry(
            stop=tnc.stop_after_attempt(retries),
            wait=tnc.wait_fixed(wait),
            retry=tnc.retry_if_exception_type(UnfinishedJob),
            reraise=True,
        )
        def update():
            job = Job.get(self.id)
            self.status = job.status
            self.updated = job.updated
            self.finished = job.finished
            self.started = job.started
            # update the results as well
            if self.status not in [JobStatus.SUCCESSFUL, JobStatus.FAILED]:
                raise UnfinishedJob

        update()


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

    def execute(self) -> Job:
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/execution")
        job_metadata = self.session.post(url, json={"inputs": self.inputs}).json()
        return Job.from_metadata(job_metadata)


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
