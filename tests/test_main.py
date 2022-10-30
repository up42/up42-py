import json
from pathlib import Path

import pytest
import pandas as pd
import requests

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    auth_live,
    credits_history_mock,
    credits_history_pagination_mock,
)
from .context import (
    main,
    get_blocks,
    get_block_details,
    get_block_coverage,
    get_credits_balance,
    get_credits_history,
    validate_manifest,
)


def test_get_blocks(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    url_get_blocks = f"{auth_mock._endpoint()}/blocks"
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
    url_get_blocks = f"{auth_mock._endpoint()}/blocks"
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
    url_get_blocks_details = f"{auth_mock._endpoint()}/blocks/{block_id}"
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
    url_get_blocks_coverage = f"{auth_mock._endpoint()}/blocks/{block_id}/coverage"
    requests_mock.get(
        url=url_get_blocks_coverage,
        json={
            "data": {
                "url": "https://storage.googleapis.com/coverage-area-interstellar-prod/coverage.json"
            },
            "error": {},
        },
    )
    url_geojson_response = (
        "https://storage.googleapis.com/coverage-area-interstellar-prod/coverage.json"
    )
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
    # pylint: disable=unused-variable
    try:
        block_id = "045019bb-06fc-4fa1-b703-318725b4d8af"
        coverage = get_block_coverage(block_id=block_id)
    except requests.exceptions.RequestException as err:
        assert True
        return
    assert False


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


def test_get_credits_history(credits_history_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", credits_history_mock)
    credits_history = get_credits_history()
    assert isinstance(credits_history, dict)
    assert "content" in credits_history
    assert isinstance(credits_history["content"], list)
    assert len(credits_history["content"]) == 10


def test_get_credits_history_pagination(credits_history_pagination_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", credits_history_pagination_mock)
    credits_history = get_credits_history()
    assert isinstance(credits_history, dict)
    assert "content" in credits_history
    assert isinstance(credits_history["content"], list)
    assert len(credits_history["content"]) == 2500


@pytest.mark.parametrize(
    "start_date,end_date",
    [(None, "2014-01-01"), ("2014-01-01", None)],
)
def test_get_credits_history_no_bounds(
    credits_history_mock, start_date, end_date, monkeypatch
):
    monkeypatch.setattr(main, "_auth", credits_history_mock)
    balance_history_no_enddate = get_credits_history(start_date=start_date)
    assert isinstance(balance_history_no_enddate, dict)
    assert "content" in balance_history_no_enddate
    assert isinstance(balance_history_no_enddate["content"], list)
    balance_history_no_startdate = get_credits_history(end_date=end_date)
    assert isinstance(balance_history_no_startdate, dict)
    assert "content" in balance_history_no_startdate
    assert isinstance(balance_history_no_startdate["content"], list)


@pytest.mark.live
def test_get_credits_history_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    balance_history = get_credits_history(
        start_date="2022-03-01", end_date="2022-03-02"
    )
    assert isinstance(balance_history, dict)
    assert "content" in balance_history
    assert len(balance_history["content"]) == 32
    assert isinstance(balance_history["content"], list)


def test_validate_manifest(auth_mock, requests_mock, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_mock)
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    url_validate_mainfest = f"{auth_mock._endpoint()}/validate-schema/block"
    requests_mock.post(
        url=url_validate_mainfest,
        json={"data": {"valid": True, "errors": []}, "error": {}},
    )

    result = validate_manifest(path_or_json=fp)
    assert result == {"valid": True, "errors": []}


@pytest.mark.live
def test_validate_manifest_valid_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    result = validate_manifest(path_or_json=fp)
    assert result == {"valid": True, "errors": []}


@pytest.mark.live
def test_validate_manifest_invalid_live(auth_live, monkeypatch):
    monkeypatch.setattr(main, "_auth", auth_live)
    fp = Path(__file__).resolve().parent / "mock_data/manifest.json"
    with open(fp) as src:
        mainfest_json = json.load(src)
        mainfest_json.update(
            {
                "_up42_specification_version": 1,
                "input_capabilities": {
                    "invalidtype": {"up42_standard": {"format": "GTiff"}}
                },
            }
        )
    with pytest.raises(requests.exceptions.RequestException):
        validate_manifest(path_or_json=mainfest_json)
