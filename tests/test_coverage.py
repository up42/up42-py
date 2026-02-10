"""
Tests for coverage module.
"""

import pytest
import requests_mock as req_mock

from tests import constants
from up42 import coverage

COVERAGE_URL = f"{constants.API_HOST}/v2/coverage/orders/{constants.ORDER_ID}"


@pytest.fixture(name="coverage_metadata")
def _coverage_metadata():
    return {
        "covered": {
            "sqKmArea": 78.5,
            "percentage": 85.0,
            "geometry": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[13.375966, 52.515068], [13.375966, 52.516068], [13.376966, 52.516068]]],
                        },
                        "properties": {},
                    }
                ],
            },
        },
        "remainder": {
            "sqKmArea": 13.8,
            "percentage": 15.0,
            "geometry": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[13.376966, 52.515068], [13.376966, 52.516068], [13.377966, 52.516068]]],
                        },
                        "properties": {},
                    }
                ],
            },
        },
    }


class TestOrderCoverage:
    def test_should_get_order_coverage(self, requests_mock: req_mock.Mocker, coverage_metadata: dict):
        requests_mock.get(url=COVERAGE_URL, json=coverage_metadata)
        order_coverage = coverage.OrderCoverage.get(order_id=constants.ORDER_ID)

        assert isinstance(order_coverage, coverage.OrderCoverage)
        assert isinstance(order_coverage.covered, coverage.GeometryMetrics)
        assert isinstance(order_coverage.remainder, coverage.GeometryMetrics)

        # Assert covered metrics
        assert order_coverage.covered.sq_km_area == 78.5
        assert order_coverage.covered.percentage == 85.0
        assert order_coverage.covered.geometry["type"] == "FeatureCollection"
        assert len(order_coverage.covered.geometry["features"]) == 1

        # Assert remainder metrics
        assert order_coverage.remainder.sq_km_area == 13.8
        assert order_coverage.remainder.percentage == 15.0
        assert order_coverage.remainder.geometry["type"] == "FeatureCollection"
        assert len(order_coverage.remainder.geometry["features"]) == 1
