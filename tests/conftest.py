from typing import cast
from unittest import mock

import pytest
import requests

from tests import constants
from up42 import host, order


@pytest.fixture(autouse=True)
def restore_default_domain():
    # To avoid breaking urls in other tests when the domain is changed in a test
    default_domain = host.DOMAIN
    yield
    host.DOMAIN = default_domain


@pytest.fixture(autouse=True)
def workspace(request):
    if "no_workspace" not in request.keywords:
        with mock.patch("up42.base.workspace") as workspace_mock:
            session = requests.Session()
            session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
            workspace_mock.session = session
            workspace_mock.id = constants.WORKSPACE_ID
            workspace_mock.auth = lambda request: request
            yield
    else:
        yield


@pytest.fixture(name="archive_order")
def _archive_order():
    return order.Order(
        id=constants.ORDER_ID,
        display_name="archive-order",
        workspace_id=constants.WORKSPACE_ID,
        account_id="account-id",
        status="CREATED",
        type="ARCHIVE",
        data_product_id=constants.DATA_PRODUCT_ID,
        tags=["some", "tags"],
        details=order.ArchiveOrderDetails(aoi={"some": "aoi"}, image_id="image-id"),
    )


@pytest.fixture(name="tasking_order")
def _tasking_order():
    return order.Order(
        id=constants.ORDER_ID,
        display_name="tasking-order",
        workspace_id=constants.WORKSPACE_ID,
        account_id="account-id",
        status="CREATED",
        type="TASKING",
        data_product_id=constants.DATA_PRODUCT_ID,
        tags=["some", "tags"],
        details=order.TaskingOrderDetails(
            acquisition_start="acquisition-start",
            acquisition_end="acquisition-end",
            geometry={"some": "geometry"},
            extra_description="extra-description",
            sub_status="FEASIBILITY_WAITING_UPLOAD",
        ),
    )


@pytest.fixture(params=["ARCHIVE", "TASKING"])
def data_order(archive_order: order.Order, tasking_order: order.Order, request):
    return {"ARCHIVE": archive_order, "TASKING": tasking_order}[request.param]


@pytest.fixture(name="archive_order_metadata")
def _archive_order_metadata(archive_order: order.Order):
    details = cast(order.ArchiveOrderDetails, archive_order.details)
    return {
        "id": constants.ORDER_ID,
        "displayName": archive_order.display_name,
        "workspaceId": constants.WORKSPACE_ID,
        "accountId": archive_order.account_id,
        "status": archive_order.status,
        "type": archive_order.type,
        "dataProductId": constants.DATA_PRODUCT_ID,
        "tags": archive_order.tags,
        "orderDetails": {"aoi": details.aoi, "imageId": details.image_id},
    }


@pytest.fixture(name="tasking_order_metadata")
def _tasking_order_metadata(tasking_order: order.Order):
    details = cast(order.TaskingOrderDetails, tasking_order.details)
    return {
        "id": constants.ORDER_ID,
        "displayName": tasking_order.display_name,
        "workspaceId": constants.WORKSPACE_ID,
        "accountId": tasking_order.account_id,
        "status": tasking_order.status,
        "type": tasking_order.type,
        "dataProductId": constants.DATA_PRODUCT_ID,
        "tags": tasking_order.tags,
        "orderDetails": {
            "acquisitionStart": details.acquisition_start,
            "acquisitionEnd": details.acquisition_end,
            "geometry": details.geometry,
            "extraDescription": details.extra_description,
            "subStatus": details.sub_status,
        },
    }


@pytest.fixture(params=["ARCHIVE", "TASKING"])
def order_metadata(archive_order_metadata: dict, tasking_order_metadata: dict, request):
    return {"ARCHIVE": archive_order_metadata, "TASKING": tasking_order_metadata}[request.param]
