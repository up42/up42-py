from typing import Dict

import pytest

from up42.utils import (
    get_logger
)

from .fixtures import (
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
