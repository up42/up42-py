import abc
import dataclasses
from typing import Optional

import pystac
import requests

import up42
from up42 import base, host, utils

logger = utils.get_logger(__name__)


pystac_client = up42.initialize_storage().pystac_client


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
    id: str

    @property
    def __job_metadata(self):
        url = host.endpoint(f"/v2/processing/jobs/{self.id}")
        try:
            job_metadata = self.session.get(url).json()
            job_results = job_metadata["results"]
            if "errors" in job_results:
                self.errors = {JobError(**error) for error in job_results["errors"]}
            return job_metadata
        except requests.HTTPError as err:
            if err.response.status_code == 422:
                errors = err.response.json()["errors"]
                self.errors = {JobError(**error) for error in errors}
            else:
                raise err

    @abc.abstractmethod
    def definition(self):
        ...

    @property
    def results(self) -> pystac.Collection:
        job_results = self.__job_metadata["results"]
        if "collection" in job_results:
            try:
                return pystac_client.get_collection(collection_id=job_results["collection"].split("/")[-1])
            except Exception as err:
                raise ValueError("Not valid STAC collection in job result.") from err
        raise ValueError("No result found for this job_id, please check status and errors.")

    @property
    def credit_consumption(self) -> Optional[JobCreditConsumption]:
        if "creditConsumption" in self.__job_metadata:
            return JobCreditConsumption(**self.__job_metadata["creditConsumption"])
        return None

    def __getattr__(self, name: str):
        metadata_key_map = {
            "process_id": "processID",
            "account_id": "accountID",
            "workspace_id": "workspaceID",
            "type": "type",
            "status": "status",
            "created": "created",
            "started": "started",
            "finished": "finished",
            "updated": "updated",
        }
        metadata_key = metadata_key_map.get(name)

        if metadata_key is None:
            raise AttributeError(f"'BaseJob' object has no attribute '{name}'")

        try:
            return self.__job_metadata[metadata_key]
        except KeyError as err:
            raise AttributeError(f"Job metadata does not contain '{metadata_key}' for '{name}'") from err
