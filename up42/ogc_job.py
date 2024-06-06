import dataclasses
import datetime
import enum
from typing import Union

import pystac
import requests

from up42 import base, host, utils

logger = utils.get_logger(__name__)


class JobResultError(ValueError):
    pass


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

    @property
    def _pystac_client(self):
        return utils.stac_client(base.workspace.auth.client.auth)

    @property
    def _job_metadata(self) -> dict:
        url = host.endpoint(f"/v2/processing/jobs/{self.id}")
        try:
            job_response = self.session.get(url)
            job_response.raise_for_status()
            return job_response.json()
        except requests.HTTPError as err:
            if err.response.status_code == 402:
                raise JobResultError(f"Job {self.id} not found") from err
            else:
                raise err

    @property
    def errors(self) -> list:
        job_results = self._job_metadata["results"]
        if "errors" in job_results:
            return [JobError(**error) for error in job_results["errors"]]
        return list()

    @property
    def collection(self) -> pystac.Collection:
        job_results = self._job_metadata["results"]
        if "collection" in job_results:
            try:
                return self._pystac_client.get_collection(collection_id=job_results["collection"].split("/")[-1])
            except Exception as err:
                raise JobResultError("Not valid STAC collection in job result.") from err
        raise JobResultError("No result found for this job_id, please check status and errors.")

    @property
    def credit_consumption(self) -> JobCreditConsumption:
        if "creditConsumption" in self._job_metadata:
            consumption_data = self._job_metadata["creditConsumption"]
            return JobCreditConsumption(
                credits=consumption_data["credits"],
                hold_id=consumption_data["holdID"],
                consumption_id=consumption_data["consumptionID"],
            )
        raise JobResultError(
            f"Job: {self.id}, has not credit consumption." "See the job status, and errors for details."
        )

    @property
    def process_id(self) -> str:
        return self._job_metadata["processID"]

    @property
    def type(self) -> str:
        return self._job_metadata["type"]

    @property
    def account_id(self) -> str:
        return self._job_metadata["accountID"]

    @property
    def job_workspace_id(self) -> str:
        return self._job_metadata["workspaceID"]

    @property
    def definition(self) -> dict:
        return self._job_metadata["definition"]

    @property
    def status(self) -> JobStatuses:
        return JobStatuses(self._job_metadata["status"])

    @property
    def created(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._job_metadata["created"].rstrip("Z"))

    @property
    def started(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._job_metadata["started"].rstrip("Z"))

    @property
    def finished(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._job_metadata["finished"].rstrip("Z"))

    @property
    def updated(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._job_metadata["updated"].rstrip("Z"))
