from typing import Dict, List

import pytest

from up42.utils import get_logger

from .fixtures import (  # pylint: disable=unused-import
    auth_credentials_live,
    workspace_live,
)

logger = get_logger(__name__)


@pytest.mark.live
def test_get_workspaces(workspace_live):
    workspace = workspace_live
    account_workspaces = workspace.get_workspaces()
    assert "content" in account_workspaces
    assert isinstance(account_workspaces, Dict)


@pytest.mark.live
def test_set_workspace_error(workspace_live):
    workspace = workspace_live
    try:
        workspace.set_workspace_id("7154-433e-9957-875f959aa69d")
    except ValueError as e:
        assert isinstance(e, ValueError)


@pytest.mark.live
def test_check_workspace(workspace_live):
    workspace = workspace_live
    try:
        workspace.get_workspace_envs()
    except ValueError as e:
        assert isinstance(e, ValueError)


@pytest.mark.live
def test_get_environments(workspace_live):
    workspace = workspace_live
    workspace.set_workspace_id("760e93fc-7154-433e-9957-875f959aa69d")
    workspace.get_workspace_envs()
    assert isinstance(workspace.environments, List)
    assert len(workspace.environments) == 1


@pytest.mark.live
def test_create_env(workspace_live):
    workspace = workspace_live
    workspace.set_workspace_id("b5933e3d-8383-4495-9b6b-73073d213c29")
    data = {"name": "test_env", "secrets": {"var1_test": "val1_test"}}
    assert data["name"] in [
        envi["name"] for envi in workspace.create_env(data).get_workspace_envs()
    ]
