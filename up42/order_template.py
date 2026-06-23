import dataclasses
from typing import Literal

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
    items: list[OrderCost | OrderError]
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
    data_product_id: str
    display_name: str
    features: geojson.FeatureCollection
    params: dict
    workspace_id: str | None = None
    tags: list[str] | None = None
    budget_id: str | None = None

    def __post_init__(self):
        if self.workspace_id is not None:
            warnings.warn(
                "`workspace_id` is deprecated and will be removed in version 5.0.0.",
                DeprecationWarning,
                stacklevel=2,
            )
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
        if self.budget_id is not None:
            payload["budgetId"] = self.budget_id
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

    def place(self) -> list[OrderReference | OrderError]:
        workspace_id = self.workspace_id or base.workspace.id
        url = host.endpoint(f"/v2/orders?workspaceId={workspace_id}")
        batch = self.session.post(url=url, json=self._payload).json()
        return _get_items(batch, OrderReference)
