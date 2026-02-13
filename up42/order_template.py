import dataclasses
from typing import Literal

import geojson  # type: ignore
import requests

from up42 import base, host, order

UnitType = Literal["SQ_KM", "SCENE"]


class EulaNotAcceptedError(Exception):
    def __init__(self, message: str, eula_id: str | None = None):
        super().__init__(message)
        self.eula_id = eula_id


class AccessRestrictedError(Exception):
    """Raised when attempting to access a restricted collection without proper permissions."""

    def __init__(self, message: str, collection: str | None = None):
        super().__init__(message)
        self.collection = collection


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
    workspace_id = base.WorkspaceId()
    data_product_id: str
    display_name: str
    features: geojson.FeatureCollection
    params: dict
    tags: list[str] | None = None

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

    def place(self) -> list[OrderReference | OrderError]:
        url = host.endpoint(f"/v2/orders?workspaceId={self.workspace_id}")
        try:
            batch = self.session.post(url=url, json=self._payload).json()
            return _get_items(batch, OrderReference)
        except requests.HTTPError as e:
            if e.response.status_code == 451:
                self._handle_eula_errors(e)
            raise e

    @staticmethod
    def _handle_eula_errors(e: requests.exceptions.HTTPError):
        try:
            print(f"error: {e.response.json()}")
            # error_body = e.response.json()
            # title = error_body.get("title", "")
            #
            # # Check if it's a EULA error
            # if "EULA" in title and "not accepted" in title:
            #     # Extract EULA ID if present
            #     eula_id = None
            #     if "EULA " in title:
            #         parts = title.split("EULA ", 1)
            #         if len(parts) > 1:
            #             eula_id = parts[1].split(" ", 1)[0]
            #     raise EulaNotAcceptedError(title, eula_id) from e
            #
            # # Check if it's an access restriction error
            # elif "Access to collection" in title and "is restricted" in title:
            #     # Extract collection name if present
            #     collection = None
            #     if "collection " in title:
            #         parts = title.split("collection ", 1)
            #         if len(parts) > 1:
            #             collection = parts[1].split(" ", 1)[0]
            #     raise AccessRestrictedError(title, collection) from e
            #
            # # Generic 451 error
            # raise EulaNotAcceptedError(title) from e
        except (ValueError, KeyError) as ex:
            # If we can't parse the error, re-raise the original
            raise ex
