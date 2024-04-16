import pytest

import up42
from up42 import catalog, main, tasking

from .fixtures import fixtures_globals as constants


def test_initialize_object_without_auth_raises():
    main._auth = None  # pylint: disable=protected-access

    with pytest.raises(RuntimeError):
        up42.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialize_storage()
    with pytest.raises(RuntimeError):
        up42.initialize_order(order_id=constants.ORDER_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_asset(asset_id=constants.ASSET_ID)


def test_global_auth_initialize_objects(
    storage_mock,
    order_mock,
    asset_mock,
):
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
    )
    catalog_obj = up42.initialize_catalog()
    assert isinstance(catalog_obj, catalog.Catalog)
    storage_obj = up42.initialize_storage()
    assert storage_obj.workspace_id == storage_mock.workspace_id
    order_obj = up42.initialize_order(order_id=constants.ORDER_ID)
    assert order_obj.info == order_mock.info
    asset_obj = up42.initialize_asset(asset_id=constants.ASSET_ID)
    assert asset_obj.info == asset_mock.info


@pytest.fixture(autouse=True)
def setup_workspace(requests_mock):
    requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
    requests_mock.get(
        url="https://api.up42.com/users/me",
        json={"data": {"id": constants.WORKSPACE_ID}},
    )


def test_should_initialize_tasking():
    up42.authenticate(
        project_id=constants.PROJECT_ID,
        project_api_key=constants.PROJECT_APIKEY,
    )
    result = up42.initialize_tasking()
    assert isinstance(result, tasking.Tasking)
