import dataclasses
from typing import Any

from up42 import base, host, utils

logger = utils.get_logger(__name__)


@dataclasses.dataclass
class GeometryMetrics:
    sq_km_area: float
    percentage: float
    geometry: dict[str, Any]

    @staticmethod
    def from_metadata(data: dict[str, Any]) -> "GeometryMetrics":
        return GeometryMetrics(
            sq_km_area=data["sqKmArea"],
            percentage=data["percentage"],
            geometry=data["geometry"],
        )


@dataclasses.dataclass
class OrderCoverage:
    session = base.Session()
    covered: GeometryMetrics
    remainder: GeometryMetrics

    @classmethod
    def get(cls, order_id: str) -> "OrderCoverage":
        url = host.endpoint(f"/v2/coverage/orders/{order_id}")
        metadata = cls.session.get(url=url).json()
        return OrderCoverage._from_metadata(metadata)

    @staticmethod
    def _from_metadata(metadata: dict) -> "OrderCoverage":
        covered = GeometryMetrics.from_metadata(metadata["covered"])
        remainder = GeometryMetrics.from_metadata(metadata["remainder"])
        return OrderCoverage(covered=covered, remainder=remainder)
