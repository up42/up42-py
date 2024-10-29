import dataclasses
from typing import Optional, Union
from unittest import mock

import pystac_client
import pytest
import requests_mock as req_mock

from up42 import base

from .fixtures import fixtures_globals as constants


class TestWorkspace:
    def test_fails_to_provide_properties_if_not_authenticated(self):
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.auth
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.id

    def test_should_authenticate(self, requests_mock):
        requests_mock.post(constants.TOKEN_ENDPOINT, json={"access_token": constants.TOKEN, "expires_in": 5 * 60})
        requests_mock.get(
            url="https://api.up42.com/users/me",
            json={"data": {"id": constants.WORKSPACE_ID}},
        )
        base.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert base.workspace.id == constants.WORKSPACE_ID

    @pytest.mark.parametrize(
        "timestamp",
        [
            None,
            "2022-12-31",
        ],
        ids=["without timestamp", "with timestamp"],
    )
    def test_should_get_credits_balance(self, requests_mock: req_mock.Mocker, timestamp: Optional[str]):
        balance_url = f"{constants.API_HOST}/v2/payments/balances"
        if timestamp:
            balance_url += "?" + f"balanceAt={timestamp}T00%3A00%3A00Z"
        balance = 10693
        requests_mock.get(
            url=balance_url,
            json={"available": {"amount": balance, "unit": "CREDIT"}},
        )
        assert base.workspace.get_credits_balance(timestamp=timestamp) == {"balance": balance}

    def test_should_fail_balance_if_timestamp_error(self):
        with pytest.raises(ValueError, match="Invalid isoformat string"):
            base.workspace.get_credits_balance(timestamp="some-error-data")


@dataclasses.dataclass(eq=True)
class ActiveRecord:
    session = base.Session()
    class_workspace_id = base.WorkspaceId()
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())
    stac_client = base.StacClient()


class TestDescriptors:
    @pytest.fixture(autouse=True)
    def workspace(self, auth_mock):
        with mock.patch("up42.base.workspace") as workspace_mock:
            workspace_mock.auth = auth_mock
            workspace_mock.id = constants.WORKSPACE_ID
            yield

    def test_should_provide_session(self):
        record = ActiveRecord()
        assert record.session == base.workspace.auth.session

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
