import abc
import dataclasses
from typing import Literal, Union

import geojson  # type: ignore

from up42 import base, host

UnitType = Literal["SQ_KM", "SCENE"]


@dataclasses.dataclass
class OrderError:
    index: int
    message: str
    details: str


@dataclasses.dataclass
class OrderReference:
    index: int
    id: str


@dataclasses.dataclass
class OrderCost:
    index: int
    credits: float
    size: float
    unit: UnitType


@dataclasses.dataclass
class BatchCost:
    items: list[Union[OrderCost, OrderError]]
    credits: float
    size: float
    unit: UnitType


def _get_items(data: dict, result_type):
    results = [result_type(**result) for result in data["results"]]
    errors = [OrderError(**error) for error in data["errors"]]
    items = results + errors
    return sorted(items, key=lambda x: x.index)


class BatchOrderTemplate:
    session = base.Session()
    workspace_id = base.WorkspaceId()

    @property
    @abc.abstractmethod
    def data_product_id(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def tags(self) -> list[str]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def features(self) -> geojson.FeatureCollection:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def params(self) -> dict:
        raise NotImplementedError

    def __post_init__(self):
        self.__validate()
        # we need to validate the schema first, then we estimate
        self.__estimate()

    @property
    def _payload(self):
        return {
            "dataProduct": self.data_product_id,
            "displayName": self.display_name,
            "tags": self.tags,
            "params": self.params,
            "featureCollection": self.features,
        }

    def __validate(self):
        # validate the schema
        # should we take schema from the data product?
        raise NotImplementedError

    def __estimate(self):
        url = host.endpoint("/v2/orders/estimate")
        estimate = self.session.post(url=url, json=self._payload).json()
        summary = estimate["summary"]
        self.cost = BatchCost(
            items=_get_items(estimate, OrderCost),
            credits=summary["totalCredits"],
            size=summary["totalSize"],
            unit=summary["unit"],
        )

    def place(self) -> list[Union[OrderReference, OrderError]]:
        url = host.endpoint(f"/v2/orders?workspaceId={self.workspace_id}")
        batch = self.session.post(url=url, json=self._payload).json()
        return _get_items(batch, OrderReference)


@dataclasses.dataclass
class ArchiveOrderTemplate(BatchOrderTemplate):
    pass


@dataclasses.dataclass
class TaskingOrderTemplate(BatchOrderTemplate):
    pass