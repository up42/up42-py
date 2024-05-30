import dataclasses
from typing import Union
from unittest import mock

import pytest

from up42 import base

from .fixtures import fixtures_globals as constants


class TestWorkspace:
    def test_fails_to_provide_properties_if_not_authenticated(self):
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.auth
        with pytest.raises(base.UserNotAuthenticated):
            _ = base.workspace.id

    def test_should_authenticate(self, requests_mock):
        requests_mock.post("https://api.up42.com/oauth/token", json={"access_token": constants.TOKEN})
        requests_mock.get(
            url="https://api.up42.com/users/me",
            json={"data": {"id": constants.WORKSPACE_ID}},
        )
        base.workspace.authenticate(username=constants.USER_EMAIL, password=constants.PASSWORD)
        assert base.workspace.id == constants.WORKSPACE_ID

    def test_should_get_credits_balance(self, requests_mock):
        balance_url = f"{constants.API_HOST}/accounts/me/credits/balance"
        balance = {"balance": 10693}
        requests_mock.get(
            url=balance_url,
            json={"data": balance},
        )
        assert base.workspace.get_credits_balance() == balance


@dataclasses.dataclass(eq=True)
class ActiveRecord:
    session = base.Session()
    workspace_id: Union[str, base.WorkspaceId] = dataclasses.field(default=base.WorkspaceId())


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

    def test_should_allow_to_set_workspace_id(self):
        record = ActiveRecord(workspace_id="custom_workspace_id")
        assert record.workspace_id == "custom_workspace_id"
        assert "custom_workspace_id" in repr(record)

    def test_should_provide_default_workspace_id(self):
        record = ActiveRecord()
        assert record.workspace_id == constants.WORKSPACE_ID
        assert constants.WORKSPACE_ID in repr(record)
