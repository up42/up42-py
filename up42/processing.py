import abc
import dataclasses
import datetime
import enum
from typing import ClassVar, Iterator, List, Optional, TypedDict, Union

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

    @classmethod
    def all(
        cls,
        process_ids: Optional[List[str]] = None,
        workspace_id: Optional[str] = None,
        statuses: Optional[List[JobStatus]] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        # can be specified via Sorting.process_id.desc & Sorting.created.asc
        # sort_by: Optional[Sorting] = None
        *,
        # used only for performance tuning and testing, affecting only limit parameter
        page_size: Optional[int],
    ) -> Iterator["Job"]:
        query_params = {
            key: str(value)
            for key, value in {
                "workspaceId": workspace_id,
                "processId": process_ids,
                "status": statuses,
                "minDuration": min_duration,
                "maxDuration": max_duration,
                "limit": page_size,
            }.items()
            if value
        }

        def get_pages():
            page = cls.session.get(
                host.endpoint("/v2/processing/jobs"), params=query_params
            ).json()
            while page:
                yield page["jobs"]
                next_page_url = next(
                    (link["href"] for link in page["links"] if link["rel"] == "next"),
                    None,
                )
                page = next_page_url and cls.session.get(next_page_url).json()

        for page in get_pages():
            for metadata in page:
                yield Job.from_metadata(metadata)
