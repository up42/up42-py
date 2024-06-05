import abc
import dataclasses
from typing import List, Union

import pystac
import requests

from up42 import base, host


@dataclasses.dataclass(eq=True, frozen=True)
class ValidationError:
    message: str
    name: str


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
        # TODO: compute cost if valid

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
