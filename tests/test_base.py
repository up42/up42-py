import dataclasses
from typing import Union

import pystac_client
import pytest
import requests_mock as req_mock

from tests import constants
from up42 import base, host

TOKEN_ENDPOINT = "https://auth.up42.com/realms/public/protocol/openid-connect/token"
SA_TOKEN_ENDPOINT = "https://auth.sa.up42.com/realms/public/protocol/openid-connect/token"
USER_INFO_ENDPOINT = "https://auth.up42.com/realms/public/protocol/openid-connect/userinfo"
SA_USER_INFO_ENDPOINT = "https://auth.sa.up42.com/realms/public/protocol/openid-connect/userinfo"


@pytest.mark.no_workspace
class TestWorkspace:
    @pytest.fixture(autouse=True)
    def reset(self):
        yield

        host.REGION = "eu"

    def test_fails_to_provide_properties_if_not_authenticated(self):
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.auth
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.id
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.session

    def test_should_authenticate(self, requests_mock):
        requests_mock.post(TOKEN_ENDPOINT, json={"access_token": constants.TOKEN, "expires_in": 5 * 60})
        requests_mock.get(url=USER_INFO_ENDPOINT, json={"sub": constants.WORKSPACE_ID})
        base.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert host.REGION == "eu"
        assert base.workspace.id == constants.WORKSPACE_ID

    def test_should_authenticate_with_region_eu(self, requests_mock):
        requests_mock.post(TOKEN_ENDPOINT, json={"access_token": constants.TOKEN, "expires_in": 5 * 60})
        requests_mock.get(url=USER_INFO_ENDPOINT, json={"sub": constants.WORKSPACE_ID})
        base.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD, region="eu")
        assert host.REGION == "eu"
        assert base.workspace.id == constants.WORKSPACE_ID

    def test_should_authenticate_with_region_sa(self, requests_mock):
        requests_mock.post(SA_TOKEN_ENDPOINT, json={"access_token": constants.TOKEN, "expires_in": 5 * 60})
        requests_mock.get(url=SA_USER_INFO_ENDPOINT, json={"sub": constants.WORKSPACE_ID})
        base.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD, region="sa")
        assert host.REGION == "sa"
        assert base.workspace.id == constants.WORKSPACE_ID


@dataclasses.dataclass(eq=True)
class ActiveRecord:
    session = base.Session()
    class_workspace_id = base.WorkspaceId()
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
    stac_client = base.StacClient()


class TestDescriptors:
    def test_should_provide_session(self):
        record = ActiveRecord()
        assert record.session == base.workspace.session

    def test_session_should_not_be_represented(self):
        assert "session" not in repr(ActiveRecord())

    def test_workspace_id_should_provide_instance_value_when_invoked_for_object(self):
        record = ActiveRecord(workspace_id="custom_workspace_id")
        assert record.workspace_id == "custom_workspace_id"
        assert record.class_workspace_id == "custom_workspace_id"
        assert ActiveRecord.class_workspace_id == constants.WORKSPACE_ID
        assert "custom_workspace_id" in repr(record)

    def test_workspace_id_should_provide_default_value(self):
        record = ActiveRecord()
        assert record.workspace_id == constants.WORKSPACE_ID
        assert ActiveRecord.class_workspace_id == constants.WORKSPACE_ID
        assert constants.WORKSPACE_ID in repr(record)

    def test_should_provide_stac_client(self, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        record = ActiveRecord()
        assert isinstance(record.stac_client, pystac_client.Client)
        assert requests_mock.called


class TestStacClient:
    def test_should_provide_stac_client(self, requests_mock: req_mock.Mocker):
        requests_mock.get(constants.URL_STAC_CATALOG, json=constants.STAC_CATALOG_RESPONSE)
        stac_client = base.stac_client()
        assert isinstance(stac_client, pystac_client.Client)
        assert requests_mock.called
