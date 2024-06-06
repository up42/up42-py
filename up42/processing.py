import abc
import dataclasses
from typing import List, Optional, Union

import pystac
import requests

from up42 import base, host


@dataclasses.dataclass(frozen=True)
class ValidationError:
    message: str
    name: str


@dataclasses.dataclass(frozen=True)
class Cost:
    strategy: str
    credits: int
    size: Optional[int] = None
    unit: Optional[str] = None

    def __le__(self, other):
        if isinstance(other, Cost):
            return self.credits <= other.credits
        else:
            return self.credits <= other

    def __lt__(self, other):
        if isinstance(other, Cost):
            return self.credits < other.credits
        else:
            return self.credits < other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other


class JobTemplate:
    session = base.Session()
    process_id: str
    title: str
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


class SingleItemJobTemplate(JobTemplate):
    item: pystac.Item

    @property
    def inputs(self) -> dict:
        return {"title": self.title, "item": self.item.get_self_href()}


class MultiItemJobTemplate(JobTemplate):
    items: List[pystac.Item]

    @property
    def inputs(self) -> dict:
        return {
            "title": self.title,
            "items": [item.get_self_href() for item in self.items],
        }
