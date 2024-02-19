"""
Note: The additional monkeypatching of the auth module in this module's tests is neccessary if running all tests
in one pytest chain.
They work without the monkeypatching when run independent of each other. However, when running all together via pytest,
e.g. `make test`, the auth module fixture is otherwise not properly attached to the class object mocks for each test,
or would need to be recreated for each test.
"""

import pandas as pd
import pytest
import requests

from up42 import main
from up42.main import get_block_coverage, get_block_details, get_blocks, get_credits_balance

from .fixtures.fixtures_globals import API_HOST


def test_get_blocks(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    url_get_blocks = f"{API_HOST}/blocks"
    requests_mock.get(
        url=url_get_blocks,
        json={
            "data": [
                {"id": "789-2736-212", "name": "tiling"},
                {"id": "789-2736-212", "name": "sharpening"},
            ],
            "error": {},
        },
    )
    blocks = get_blocks()
    assert isinstance(blocks, dict)
    assert "tiling" in list(blocks.keys())


@pytest.mark.live
def test_get_blocks_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    blocks = get_blocks(basic=False)
    assert isinstance(blocks, list)
    blocknames = [block["name"] for block in blocks]
    assert "tiling" in blocknames


def test_get_blocks_not_basic_dataframe(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    url_get_blocks = f"{API_HOST}/blocks"
    json_get_blocks = {
        "data": [
            {"id": "789-2736-212", "name": "tiling"},
            {"id": "789-2736-212", "name": "sharpening"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_get_blocks, json=json_get_blocks)

    blocks_df = get_blocks(basic=False, as_dataframe=True)
    assert isinstance(blocks_df, pd.DataFrame)
    assert "tiling" in blocks_df["name"].to_list()


def test_get_block_details(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    block_id = "273612-13"
    url_get_blocks_details = f"{API_HOST}/blocks/{block_id}"
    requests_mock.get(
        url=url_get_blocks_details,
        json={
            "data": {"id": "273612-13", "name": "tiling", "createdAt": "123"},
            "error": {},
        },
    )
    details = get_block_details(block_id=block_id)
    assert isinstance(details, dict)
    assert details["id"] == block_id
    assert "createdAt" in details


@pytest.mark.live
def test_get_block_details_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    tiling_id = "3e146dd6-2b67-4d6e-a422-bb3d973e32ff"

    details = get_block_details(block_id=tiling_id)
    assert isinstance(details, dict)
    assert details["id"] == tiling_id
    assert "createdAt" in details


def test_get_block_coverage(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    block_id = "273612-13"
    url_get_blocks_coverage = f"{API_HOST}/blocks/{block_id}/coverage"
    requests_mock.get(
        url=url_get_blocks_coverage,
        json={
            "data": {"url": "https://storage.googleapis.com/coverage-area-interstellar-prod/coverage.json"},
            "error": {},
        },
    )
    url_geojson_response = "https://storage.googleapis.com/coverage-area-interstellar-prod/coverage.json"
    requests_mock.get(
        url=url_geojson_response,
        json={
            "type": "FeatureCollection",
            "name": "bundle6m",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "MultiPolygon", "coordinates": []},
                }
            ],
        },
    )
    coverage = get_block_coverage(block_id=block_id)
    assert isinstance(coverage, dict)
    assert "features" in coverage


@pytest.mark.live
def test_get_block_coverage_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    block_id = "625fd923-8ae6-4ac3-8e13-f51d3c977222"
    coverage = get_block_coverage(block_id=block_id)
    assert isinstance(coverage, dict)
    assert "features" in coverage


@pytest.mark.live
def test_get_block_coverage_noresults_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    with pytest.raises(requests.exceptions.RequestException):
        block_id = "045019bb-06fc-4fa1-b703-318725b4d8af"
        get_block_coverage(block_id=block_id)


def test_get_credits_balance(auth_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    balance = get_credits_balance()
    assert isinstance(balance, dict)
    assert "balance" in balance


@pytest.mark.live
def test_get_credits_balance_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    balance = get_credits_balance()
    assert isinstance(balance, dict)
    assert "balance" in balance


def test_get_auth_safely_no_auth(monkeypatch):
    monkeypatch.setattr(main, "_auth", None)
    with pytest.raises(ValueError) as excinfo:
        main.__get_auth_safely()
    assert "User not authenticated. Call up42.authenticate() first" in str(excinfo.value)


def test_get_webhook_events(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    url_webhook_events = f"{API_HOST}/webhooks/events"
    requests_mock.get(
        url=url_webhook_events,
        json={
            "data": ["some event"],
            "error": {},
        },
    )
    events = main.get_webhook_events()
    assert isinstance(events, list)
    assert "some event" in events
