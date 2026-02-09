import requests_mock as req_mock

from up42 import coverage


def test_order_coverage_get():
    api_response = {
        "covered": {
            "sqKmArea": 12.0,
            "percentage": 60.0,
            "geometry": {"type": "FeatureCollection", "features": [{"id": 1}]},
        },
        "remainder": {
            "sqKmArea": 8.0,
            "percentage": 40.0,
            "geometry": {"type": "FeatureCollection", "features": [{"id": 2}]},
        },
    }
    order_id = "test-order-id"
    url = f"https://api.up42.com/v2/coverage/orders/{order_id}"
    with req_mock.Mocker() as m:
        m.get(url, json=api_response)
        res = coverage.OrderCoverage.get(order_id)
        assert hasattr(res, "covered")
        assert hasattr(res, "remainder")
        assert hasattr(res.covered, "sq_km_area")
        assert hasattr(res.covered, "percentage")
        assert hasattr(res.covered, "geometry")
        assert res.covered.sq_km_area == 12.0
        assert res.covered.percentage == 60.0
        assert res.covered.geometry["type"] == "FeatureCollection"
        assert res.covered.geometry["features"] == [{"id": 1}]
        assert res.remainder.sq_km_area == 8.0
        assert res.remainder.percentage == 40.0
        assert res.remainder.geometry["type"] == "FeatureCollection"
        assert res.remainder.geometry["features"] == [{"id": 2}]
