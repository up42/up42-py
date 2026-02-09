import dataclasses
from typing import Any

from up42 import base, host, utils

logger = utils.get_logger(__name__)


@dataclasses.dataclass
class GeometryMetrics:
    sq_km_area: float
    percentage: float
    geometry: dict[str, Any]


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
        covered = GeometryMetrics(
            metadata["covered"]["sqKmArea"], metadata["covered"]["percentage"], metadata["covered"]["geometry"]
        )
        remainder = GeometryMetrics(
            metadata["remainder"]["sqKmArea"], metadata["remainder"]["percentage"], metadata["remainder"]["geometry"]
        )
        return OrderCoverage(covered=covered, remainder=remainder)
