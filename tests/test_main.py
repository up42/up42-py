import pandas as pd
import pytest
import requests

from up42 import main

from .fixtures import fixtures_globals


@pytest.fixture(autouse=True)
def setup_auth_mock(auth_mock):
    main.Main.set_auth(auth_mock)
    yield


def test_get_blocks(auth_mock, requests_mock):
    url_get_blocks = f"{fixtures_globals.API_HOST}/blocks"
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
    main.Main().set_auth(auth_mock)
    blocks = main.get_blocks()
    assert isinstance(blocks, dict)
    assert "tiling" in list(blocks.keys())


@pytest.mark.live
def test_get_blocks_live(auth_live):
    main.Main.set_auth(auth_live)
    blocks = main.get_blocks(basic=False)
    assert isinstance(blocks, list)
    blocknames = [block["name"] for block in blocks]
    assert "tiling" in blocknames


def test_get_blocks_not_basic_dataframe(auth_mock, requests_mock):
    url_get_blocks = f"{fixtures_globals.API_HOST}/blocks"
    json_get_blocks = {
        "data": [
            {"id": "789-2736-212", "name": "tiling"},
            {"id": "789-2736-212", "name": "sharpening"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_get_blocks, json=json_get_blocks)

    blocks_df = main.get_blocks(basic=False, as_dataframe=True)
    assert isinstance(blocks_df, pd.DataFrame)
    assert "tiling" in blocks_df["name"].to_list()


def test_get_block_details(auth_mock, requests_mock):
    block_id = "273612-13"
    url_get_blocks_details = f"{fixtures_globals.API_HOST}/blocks/{block_id}"
    requests_mock.get(
        url=url_get_blocks_details,
        json={
            "data": {"id": "273612-13", "name": "tiling", "createdAt": "123"},
            "error": {},
        },
    )
    details = main.get_block_details(block_id=block_id)
    assert isinstance(details, dict)
    assert details["id"] == block_id
    assert "createdAt" in details


@pytest.mark.live
def test_get_block_details_live(auth_live):
    main.Main.set_auth(auth_live)
    tiling_id = "3e146dd6-2b67-4d6e-a422-bb3d973e32ff"

    details = main.get_block_details(block_id=tiling_id)
    assert isinstance(details, dict)
    assert details["id"] == tiling_id
    assert "createdAt" in details


def test_get_block_coverage(auth_mock, requests_mock):
    block_id = "273612-13"
    url_get_blocks_coverage = (
        f"{fixtures_globals.API_HOST}/blocks/{block_id}/coverage"
    )
    requests_mock.get(
        url=url_get_blocks_coverage,
        json={
            "data": {
                "url": "https://storage.googleapis.com/coverage-area-interstellar-prod/coverage.json"
            },
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
    coverage = main.get_block_coverage(block_id=block_id)
    assert isinstance(coverage, dict)
    assert "features" in coverage


@pytest.mark.live
def test_get_block_coverage_live(auth_live):
    main.Main.set_auth(auth_live)
    block_id = "625fd923-8ae6-4ac3-8e13-f51d3c977222"
    coverage = main.get_block_coverage(block_id=block_id)
    assert isinstance(coverage, dict)
    assert "features" in coverage


@pytest.mark.live
def test_get_block_coverage_noresults_live(auth_live):
    main.Main.set_auth(auth_live)
    with pytest.raises(requests.exceptions.RequestException):
        block_id = "045019bb-06fc-4fa1-b703-318725b4d8af"
        main.get_block_coverage(block_id=block_id)


def test_get_credits_balance(auth_mock):
    balance = main.get_credits_balance()
    assert isinstance(balance, dict)
    assert "balance" in balance


@pytest.mark.live
def test_get_credits_balance_live(auth_live):
    main.Main.set_auth(auth_live)
    balance = main.get_credits_balance()
    assert isinstance(balance, dict)
    assert "balance" in balance


def test_fails_to_get_auth_safely_if_unauthenticated():
    main.Main().set_auth(None)
    with pytest.raises(ValueError):
        main.Main().get_auth_safely()


def test_get_webhook_events(setup_auth_mock, requests_mock):
    url_webhook_events = f"{fixtures_globals.API_HOST}/webhooks/events"
    events = ["some-event"]
    requests_mock.get(
        url=url_webhook_events,
        json={
            "data": events,
            "error": {},
        },
    )
    assert main.get_webhook_events() == events


@pytest.mark.parametrize("return_json", [False, True])
def test_get_webhooks(setup_auth_mock, webhooks_mock, return_json):
    webhooks = main.get_webhooks(return_json=return_json)
    expected = webhooks_mock.get_webhooks(return_json=return_json)
    if return_json:
        assert webhooks == expected
    else:
        for hook, expected_hook in zip(webhooks, expected):
            assert hook.webhook_id == expected_hook.webhook_id
            assert hook._info == expected_hook._info
