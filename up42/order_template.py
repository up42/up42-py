import dataclasses
from typing import Literal, Optional, Union

import geojson  # type: ignore

from up42 import base, host, order

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

    @property
    def order(self):
        return order.Order.get(self.id)


@dataclasses.dataclass
class OrderCost:
    index: int
    credits: float
    size: float
    unit: UnitType


@dataclasses.dataclass
class Estimate:
    items: list[Union[OrderCost, OrderError]]
    credits: float
    size: float
    unit: UnitType


def _get_items(data: dict, result_type):
    results = [result_type(**result) for result in data["results"]]
    errors = [OrderError(**error) for error in data["errors"]]
    items = results + errors
    return sorted(items, key=lambda x: x.index)


@dataclasses.dataclass
class BatchOrderTemplate:
    session = base.Session()
    workspace_id = base.WorkspaceId()
    data_product_id: str
    display_name: str
    features: geojson.FeatureCollection
    params: dict
    tags: Optional[list[str]] = None

    def __post_init__(self):
        self.__estimate()

    @property
    def _payload(self):
        payload = {
            "dataProduct": self.data_product_id,
            "displayName": self.display_name,
            "params": self.params,
            "featureCollection": self.features,
        }
        if self.tags is not None:
            payload["tags"] = self.tags
        return payload

    def __estimate(self):
        url = host.endpoint("/v2/orders/estimate")
        estimate = self.session.post(url=url, json=self._payload).json()
        summary = estimate["summary"]
        self.estimate = Estimate(
            items=_get_items(estimate, OrderCost),
            credits=summary["totalCredits"],
            size=summary["totalSize"],
            unit=summary["unit"],
        )

    def place(self) -> list[Union[OrderReference, OrderError]]:
        url = host.endpoint(f"/v2/orders?workspaceId={self.workspace_id}")
        batch = self.session.post(url=url, json=self._payload).json()
        return _get_items(batch, OrderReference)
