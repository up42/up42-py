import abc
import dataclasses
import datetime
import enum
from typing import ClassVar, TypedDict
from collections.abc import Iterator

import pystac
import requests
import tenacity as tnc

from up42 import base, host, utils

ISO_FORMAT_LENGTH = 23  # precision including milliseconds


@dataclasses.dataclass(frozen=True)
class ValidationError:
    message: str
    name: str


class JobStatus(enum.Enum):
    CREATED = "created"
    LICENSED = "licensed"
    UNLICENSED = "unlicensed"
    VALID = "valid"
    INVALID = "invalid"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CAPTURED = "captured"
    RELEASED = "released"


TERMINAL_STATUSES = [
    JobStatus.CAPTURED,
    JobStatus.RELEASED,
    JobStatus.INVALID,
    JobStatus.REJECTED,
    JobStatus.UNLICENSED,
]


class JobResults(TypedDict, total=False):
    collection: str | None
    errors: list[dict] | None


class JobMetadata(TypedDict):
    # pylint: disable=invalid-name
    processID: str
    jobID: str
    accountID: str
    workspaceID: str | None
    definition: dict
    results: JobResults | None
    creditConsumption: dict | None
    status: str
    created: str
    started: str | None
    finished: str | None
    updated: str


class UnfinishedJob(Exception):
    """Job hasn't finished yet with success or failure"""


class JobSorting:
    process_id = utils.SortingField("processID")
    status = utils.SortingField("status", ascending=False)
    created = utils.SortingField("created", ascending=False)
    credits = utils.SortingField("creditConsumption.credits", ascending=False)


def _to_datetime(value: str | None):
    return value and datetime.datetime.fromisoformat(value[:ISO_FORMAT_LENGTH])


@dataclasses.dataclass
class Job:
    session = base.Session()
    stac_client = base.StacClient()
    process_id: str
    id: str
    account_id: str
    workspace_id: str | None
    definition: dict
    status: JobStatus
    created: datetime.datetime
    updated: datetime.datetime
    collection_url: str | None = None
    errors: list[ValidationError] | None = None
    credits: int | None = None
    started: datetime.datetime | None = None
    finished: datetime.datetime | None = None

    @property
    def collection(self) -> pystac.Collection | None:
        if self.collection_url is None:
            return None
        collection_id = self.collection_url.split("/")[-1]
        return self.stac_client.get_collection(collection_id)

    @staticmethod
    def from_metadata(metadata: JobMetadata) -> "Job":
        results: JobResults = metadata.get("results") or {}
        errors = results.get("errors") or []
        validation_errors = [ValidationError(**error) for error in errors]
        consumption = metadata.get("creditConsumption") or {}
        return Job(
            process_id=metadata["processID"],
            id=metadata["jobID"],
            account_id=metadata["accountID"],
            workspace_id=metadata["workspaceID"],
            collection_url=results.get("collection"),
            errors=validation_errors or None,
            credits=consumption.get("credits"),
            definition=metadata["definition"],
            status=JobStatus(metadata["status"]),
            created=_to_datetime(metadata["created"]),
            started=_to_datetime(metadata["started"]),
            finished=_to_datetime(metadata["finished"]),
            updated=_to_datetime(metadata["updated"]),
        )

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
            self.collection_url = job.collection_url
            self.errors = job.errors
            self.credits = job.credits
            if self.status not in TERMINAL_STATUSES:
                raise UnfinishedJob

        update()

    @classmethod
    def get(cls, job_id: str) -> "Job":
        url = host.endpoint(f"/v2/processing/jobs/{job_id}")
        metadata = cls.session.get(url).json()
        return cls.from_metadata(metadata)

    @classmethod
    def all(
        cls,
        process_id: list[str] | None = None,
        workspace_id: str | None = None,
        status: list[JobStatus] | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
        sort_by: utils.SortingField | None = None,
        ids: list[str] | None = None,
        *,
        # used for performance tuning and testing only
        page_size: int | None = None,
    ) -> Iterator["Job"]:
        query_params = {
            key: str(value)
            for key, value in {
                "workspaceId": workspace_id,
                "processId": ",".join(process_id) if process_id else None,
                "status": ",".join(entry.value for entry in status) if status else None,
                "minDuration": min_duration,
                "maxDuration": max_duration,
                "limit": page_size,
                "sort": sort_by,
                "ids": ",".join(ids) if ids else None,
            }.items()
            if value
        }

        def get_pages():
            page = cls.session.get(host.endpoint("/v2/processing/jobs"), params=query_params).json()
            while page:
                yield page["jobs"]
                next_page_url = next(
                    (link["href"] for link in page["links"] if link["rel"] == "next"),
                    None,
                )
                page = next_page_url and cls.session.get(host.endpoint(next_page_url)).json()

        for page in get_pages():
            for metadata in page:
                yield Job.from_metadata(metadata)


@dataclasses.dataclass(frozen=True)
class Cost:
    strategy: str
    credits: int
    size: int | None = None
    unit: str | None = None

    def __le__(self, other: "CostType"):
        if isinstance(other, Cost):
            return self.credits <= other.credits
        else:
            return self.credits <= other

    def __lt__(self, other: "CostType"):
        if isinstance(other, Cost):
            return self.credits < other.credits
        else:
            return self.credits < other

    def __ge__(self, other: "CostType"):
        return not self < other

    def __gt__(self, other: "CostType"):
        return not self <= other


CostType = int | float | Cost


class JobTemplate:
    session = base.Session()
    process_id: ClassVar[str]
    workspace_id: str | base.WorkspaceId
    errors: set[ValidationError] = set()
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

    def __validate_process_exists(self) -> set[ValidationError]:
        process_url = host.endpoint(f"/v2/processing/processes/{self.process_id}")
        try:
            self.process_description = self.session.get(process_url).json()
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                return {
                    ValidationError(
                        name="ProcessNotFound",
                        message=f"The process {self.process_id} does not exist.",
                    )
                }
            else:
                raise err
        return set()

    def __validate_eula(self) -> set[ValidationError]:
        eula_id = next(
            parameter["value"][0]
            for parameter in self.process_description["additionalParameters"]["parameters"]
            if parameter["name"] == "eula-id"
        )
        eula_url = host.endpoint(f"/v2/eulas/{eula_id}")
        eula = self.session.get(eula_url).json()
        if not eula["isAccepted"]:
            return {
                ValidationError(
                    name="EulaNotAccepted",
                    message=f"EULA for the process {self.process_id} not accepted.",
                )
            }
        return set()

    def __validate_inputs(self) -> set[ValidationError]:
        url = host.endpoint(f"/v2/processing/processes/{self.process_id}/validation")
        try:
            _ = self.session.post(url, json={"inputs": self.inputs})
        except requests.HTTPError as err:
            if (status_code := err.response.status_code) in (400, 422):
                if status_code == 400:
                    return {
                        ValidationError(
                            name="InvalidSchema",
                            message=err.response.json()["schema-error"],
                        )
                    }
                if status_code == 422:
                    errors = err.response.json()["errors"]
                    return {ValidationError(**error) for error in errors}
            else:
                raise err
        return set()

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
        job_metadata = self.session.post(
            url, params={"workspaceId": self.workspace_id}, json={"inputs": self.inputs}
        ).json()
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
    items: list[pystac.Item]

    @property
    def inputs(self) -> dict:
        return {
            "title": self.title,
            "items": [item.get_self_href() for item in self.items],
        }
