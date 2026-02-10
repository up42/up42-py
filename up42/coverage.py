"""
Coverage functionality for tasking orders.
"""

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
        covered_data = metadata["covered"]
        remainder_data = metadata["remainder"]

        covered = GeometryMetrics(
            sq_km_area=covered_data["sqKmArea"],
            percentage=covered_data["percentage"],
            geometry=covered_data["geometry"],
        )

        remainder = GeometryMetrics(
            sq_km_area=remainder_data["sqKmArea"],
            percentage=remainder_data["percentage"],
            geometry=remainder_data["geometry"],
        )

        return OrderCoverage(covered=covered, remainder=remainder)
