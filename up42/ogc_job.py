import dataclasses
import datetime
import enum
from typing import Union

import pystac
import requests

from up42 import base, host, utils

logger = utils.get_logger(__name__)


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


@dataclasses.dataclass(eq=True)
class JobError:
    message: str
    name: str


@dataclasses.dataclass(eq=True, frozen=True)
class JobCreditConsumption:
    credits: int
    hold_id: str
    consumption_id: str


class BaseJob:
    session = base.Session()
    workspace_id: Union[str, base.WorkspaceId]
    id: str

    pystac_client = utils.stac_client(base.workspace.auth.client.auth)

    @property
    def __job_metadata(self) -> dict:
        url = host.endpoint(f"/v2/processing/jobs/{self.id}")
        try:
            job_response = self.session.get(url)
            job_response.raise_for_status()
            if "errors" in (job_results := job_response.json()["results"]):
                self.errors = {JobError(**error) for error in job_results["errors"]}
            return job_response.json()
        except requests.HTTPError as err:
            if err.response.status_code == 402:
                raise ValueError(f"Job {self.id} not found") from err
            else:
                raise err

    @property
    def results(self) -> pystac.Collection:
        job_results = self.__job_metadata["results"]
        if "collection" in job_results:
            try:
                return self.pystac_client.get_collection(collection_id=job_results["collection"].split("/")[-1])
            except Exception as err:
                raise ValueError("Not valid STAC collection in job result.") from err
        raise ValueError("No result found for this job_id, please check status and errors.")

    @property
    def credit_consumption(self) -> JobCreditConsumption:
        if "creditConsumption" in self.__job_metadata:
            return JobCreditConsumption(**self.__job_metadata["creditConsumption"])
        raise ValueError(f"Job: {self.id}, has not credit consumption." "See the job status, and errors for details.")

    @property
    def process_id(self) -> str:
        return self.__job_metadata["processID"]

    @property
    def type(self) -> str:
        return self.__job_metadata["type"]

    @property
    def account_id(self) -> str:
        return self.__job_metadata["accountID"]

    @property
    def job_workspace_id(self) -> str:
        return self.__job_metadata["workspaceID"]

    @property
    def definition(self) -> dict:
        return self.__job_metadata["definition"]

    @property
    def status(self) -> JobStatuses:
        return JobStatuses(self.__job_metadata["status"])

    @property
    def created(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.__job_metadata["created"].rstrip("Z"))

    @property
    def started(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.__job_metadata["started"].rstrip("Z"))

    @property
    def finished(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.__job_metadata["finished"].rstrip("Z"))

    @property
    def updated(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.__job_metadata["updated"].rstrip("Z"))
