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
    data = {"name": "test_env_create", "secrets": {"var1_test": "val1_test"}}
    assert data["name"] in [
        envon["name"] for envon in workspace.create_env(data).get_workspace_envs()
    ]
    for env_obj in workspace.get_workspace_envs():
        if data["name"] == env_obj["name"]:
            workspace.delete_env(env_obj["id"])


@pytest.mark.live
def test_delete_env(workspace_live):
    workspace = workspace_live
    environment_id = None
    workspace.set_workspace_id("b5933e3d-8383-4495-9b6b-73073d213c29")
    data = {"name": "test_env_delete", "secrets": {"var1_test": "val1_test"}}
    workspace_envs = workspace.create_env(data).get_workspace_envs()
    for env_obj in workspace_envs:
        if data["name"] == env_obj["name"]:
            environment_id = env_obj["id"]
    if environment_id is not None:
        assert environment_id not in [
            envon["id"]
            for envon in workspace.delete_env(environment_id).get_workspace_envs()
        ]
    else:
        raise ValueError("env_id not found. Please check create_env method")


@pytest.mark.live
def test_delete_unknown_env(workspace_live):
    workspace = workspace_live
    environment_id = "something_random"
    try:
        workspace.delete_env(environment_id)
    except ValueError as e:
        assert isinstance(e, ValueError)
