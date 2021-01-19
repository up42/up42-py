import os
import pytest

# pylint: disable=unused-import
from .context import Order
from .fixtures import (
    ASSET_ID,
    JSON_ORDER,
    ORDER_ID,
    WORKSPACE_ID,
    auth_mock,
    auth_live,
    order_mock,
    order_live,
)


def test_init(order_mock):
    assert isinstance(order_mock, Order)
    assert order_mock.order_id == ORDER_ID
    assert order_mock.workspace_id == WORKSPACE_ID


def test_order_info(order_mock):
    assert order_mock.info
    assert order_mock.info["id"] == ORDER_ID
    assert order_mock.info["dataProvider"] == JSON_ORDER["data"]["dataProvider"]
    assert order_mock.info["assets"][0] == ASSET_ID


@pytest.mark.live
def test_order_info_live(order_live):
    assert order_live.info
    assert order_live.info["id"] == os.getenv("TEST_UP42_ORDER_ID")
    assert order_live.info["dataProvider"] == "OneAtlas"


# pylint: disable=unused-argument
@pytest.mark.parametrize("status", ["PLACED", "FULFILLED"])
def test_order_status(order_mock, status, monkeypatch):
    monkeypatch.setattr(Order, "info", {"status": status})
    assert order_mock.status == status


# pylint: disable=unused-argument
@pytest.mark.parametrize(
    "status,expected",
    [("NOT STARTED", False), ("PLACED", False), ("FULFILLED", True)],
)
def test_is_fulfilled(order_mock, status, expected, monkeypatch):
    monkeypatch.setattr(Order, "info", {"status": status})
    assert order_mock.is_fulfilled == expected


def test_order_metadata(order_mock):
    assert order_mock.metadata
    assert order_mock.metadata["id"] == ORDER_ID
    assert order_mock.metadata["sqKmArea"] == 0.1


@pytest.mark.live
def test_order_metadata_live(order_live):
    assert order_live.metadata
    assert order_live.metadata["id"] == os.getenv("TEST_UP42_ORDER_ID")
