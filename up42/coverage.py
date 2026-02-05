import dataclasses
from typing import Any

from up42 import base, host


@dataclasses.dataclass
class Geometry:
    type: str
    coordinates: list

    @staticmethod
    def from_dict(obj: dict) -> "Geometry":
        return Geometry(type=obj["type"], coordinates=obj["coordinates"])


@dataclasses.dataclass
class Feature:
    type: str
    geometry: Geometry
    properties: dict[str, Any] | None = None

    @staticmethod
    def from_dict(obj: dict) -> "Feature":
        return Feature(type=obj["type"], geometry=Geometry.from_dict(obj["geometry"]), properties=obj.get("properties"))


@dataclasses.dataclass
class FeatureCollection:
    type: str
    features: list[Feature]

    @staticmethod
    def from_dict(obj: dict) -> "FeatureCollection":
        return FeatureCollection(type=obj["type"], features=[Feature.from_dict(f) for f in obj["features"]])


@dataclasses.dataclass
class GeometryMetrics:
    sq_km_area: float
    percentage: float
    geometry: FeatureCollection

    @staticmethod
    def from_dict(obj: dict) -> "GeometryMetrics":
        return GeometryMetrics(
            sq_km_area=obj["sqKmArea"],
            percentage=obj["percentage"],
            geometry=FeatureCollection.from_dict(obj["geometry"]),
        )


@dataclasses.dataclass
class OrderDeliveryMetrics:
    covered: GeometryMetrics
    remainder: GeometryMetrics

    @staticmethod
    def from_dict(obj: dict) -> "OrderDeliveryMetrics":
        return OrderDeliveryMetrics(
            covered=GeometryMetrics.from_dict(obj["covered"]), remainder=GeometryMetrics.from_dict(obj["remainder"])
        )


class Coverage:
    session = base.Session()

    def __init__(self, base_url: str, bearer_token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}

    @classmethod
    def get(cls, order_id: str) -> OrderDeliveryMetrics:
        url = host.endpoint(f"/v2/coverage/orders/{order_id}")
        metadata = cls.session.get(url=url).json()
        return OrderDeliveryMetrics.from_dict(metadata)
