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
def test_get_environments(workspace_live):
    workspace = workspace_live
    workspace.set_workspace_id("760e93fc-7154-433e-9957-875f959aa69d")
    workspace.get_workspace_envs()
    assert isinstance(workspace.environments, List)
    assert len(workspace.environments) == 1
